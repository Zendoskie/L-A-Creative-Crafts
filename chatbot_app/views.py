from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import time
import logging
import requests

logger = logging.getLogger(__name__)

# AI API Configuration (OpenRouter)
# Load from settings dynamically in function to ensure latest values

# System prompt for the chatbot
SYSTEM_PROMPT = """You are a helpful and friendly customer service chatbot for L&A Creative Crafts, a business specializing in Handmade Crafts & Accessories. 

Your role is to:
- Answer questions about L&A Creative Crafts products and services
- Provide information about handmade crafts and accessories
- Assist customers with inquiries about orders, products, and the business
- Be friendly, professional, and helpful

Keep your responses concise, warm, and customer-service oriented. Always represent L&A Creative Crafts in a positive light."""

def intro_view(request):
    """Welcome/intro page view"""
    return render(request, 'chatbot_app/intro.html')

def chat_view(request):
    """Main chat page view"""
    return render(request, 'chatbot_app/chat.html')

@csrf_protect
@require_http_methods(["POST"])
def chat_api(request):
    """API endpoint for handling chat messages"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Load API configuration from settings dynamically
        ai_api_url = getattr(settings, 'AI_API_URL', 'https://openrouter.ai/api/v1/chat/completions')
        ai_api_key = getattr(settings, 'AI_API_KEY', '')
        ai_model = getattr(settings, 'AI_MODEL', 'deepseek/deepseek-chat')
        
        if not ai_api_key:
            logger.error("AI_API_KEY is not configured in settings")
            return JsonResponse({
                'error': 'API key is not configured. Please check your settings.',
                'status': 'error'
            }, status=500)
        
        # Get conversation history from session, or initialize it
        if 'conversation_history' not in request.session:
            request.session['conversation_history'] = []
        
        conversation_history = request.session['conversation_history']
        
        # Add user message to conversation history
        conversation_history.append({'role': 'user', 'content': user_message})
        
        # Build messages array with system prompt and conversation history
        # Keep conversation history reasonable length (last 20 messages to avoid token limits)
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        messages.extend(conversation_history[-20:])  # Keep last 20 messages
        
        # Prepare request to AI API (OpenRouter)
        headers = {
            'Authorization': f'Bearer {ai_api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': request.build_absolute_uri('/'),  # For OpenRouter tracking
            'X-Title': 'L&A Creative Crafts Chatbot'  # For OpenRouter tracking
        }
        
        # Log headers (without full API key)
        logger.debug(f"Request headers: {dict((k, v if k != 'Authorization' else v[:30] + '...') for k, v in headers.items())}")
        
        logger.info(f"Sending request to {ai_api_url} with model {ai_model}")
        
        payload = {
            'model': ai_model,
            'messages': messages,
            'stream': False,
            'temperature': 0.7,
            'top_p': 0.8
        }
        
        # Make request with retry logic
        max_retries = 3
        retry_delay = 1
        response = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Making request to AI API (attempt {attempt + 1}/{max_retries})")
                logger.info(f"API Key: {ai_api_key[:20]}... (length: {len(ai_api_key) if ai_api_key else 0})")
                logger.info(f"Payload model: {payload['model']}, messages count: {len(payload['messages'])}")
                
                api_response = requests.post(
                    ai_api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                logger.info(f"API Response Status: {api_response.status_code}")
                
                # Check if request was successful
                if api_response.status_code == 200:
                    response_data = api_response.json()
                    
                    # Extract the response message
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        ai_response = response_data['choices'][0]['message']['content'].strip()
                        
                        if not ai_response:
                            raise ValueError("Empty response from AI API")
                        
                        # Add assistant response to conversation history
                        conversation_history.append({'role': 'assistant', 'content': ai_response})
                        
                        # Update session with conversation history
                        request.session['conversation_history'] = conversation_history
                        request.session.modified = True
                        
                        logger.info("Successfully received response from AI API")
                        return JsonResponse({
                            'response': ai_response,
                            'status': 'success'
                        })
                    else:
                        raise ValueError("Unexpected response format from AI API")
                
                # Handle rate limiting (429)
                elif api_response.status_code == 429:
                    if attempt < max_retries - 1:
                        # Try to get retry-after header
                        retry_after = api_response.headers.get('Retry-After')
                        if retry_after:
                            try:
                                retry_delay = int(retry_after) + 1
                            except:
                                retry_delay = min(retry_delay * 2, 60)
                        else:
                            retry_delay = min(retry_delay * 2, 60)
                        
                        logger.warning(f"Rate limit error, retrying in {retry_delay}s")
                        time.sleep(retry_delay)
                        continue
                    else:
                        return JsonResponse({
                            'error': 'API rate limit exceeded. Please wait a moment and try again.',
                            'status': 'error'
                        }, status=429)
                
                # Handle authentication errors (401)
                elif api_response.status_code == 401:
                    error_data = api_response.json() if api_response.headers.get('content-type', '').startswith('application/json') else {}
                    error_message = error_data.get('error', {}).get('message', api_response.text) if error_data else api_response.text
                    logger.error(f"API authentication failed: {error_message}")
                    logger.error(f"Response status: {api_response.status_code}, Response text: {api_response.text[:500]}")
                    return JsonResponse({
                        'error': f'API authentication failed: {error_message[:200] if error_message else "Please check your API key"}',
                        'status': 'error'
                    }, status=401)
                
                # Handle other errors
                else:
                    error_data = api_response.json() if api_response.headers.get('content-type', '').startswith('application/json') else {}
                    error_message = error_data.get('error', {}).get('message', api_response.text) if error_data else api_response.text
                    logger.error(f"AI API error {api_response.status_code}: {error_message}")
                    
                    if attempt < max_retries - 1:
                        retry_delay = min(retry_delay * 2, 60)
                        time.sleep(retry_delay)
                        continue
                    else:
                        return JsonResponse({
                            'error': f'API error: {error_message[:200]}',
                            'status': 'error'
                        }, status=api_response.status_code)
            
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    retry_delay = min(retry_delay * 2, 60)
                    time.sleep(retry_delay)
                    continue
                else:
                    return JsonResponse({
                        'error': 'Request timeout. Please try again.',
                        'status': 'error'
                    }, status=504)
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {str(e)}")
                if attempt < max_retries - 1:
                    retry_delay = min(retry_delay * 2, 60)
                    time.sleep(retry_delay)
                    continue
            else:
                    return JsonResponse({
                        'error': f'Network error: {str(e)[:200]}',
                        'status': 'error'
                    }, status=500)
        
        # If we exhausted all retries
        return JsonResponse({
            'error': 'Failed to get response from API after multiple attempts',
            'status': 'error'
        }, status=500)
        
    except ValueError as e:
        logger.error(f"Value error in chat_api: {str(e)}")
        return JsonResponse({
            'error': f'Invalid response format: {str(e)}',
            'status': 'error'
        }, status=500)
    
    except Exception as e:
        error_str = str(e)
        logger.error(f"Error in chat_api: {error_str}", exc_info=True)
        
        # Provide user-friendly error messages
        if '429' in error_str or 'rate limit' in error_str.lower():
            user_message = "API rate limit exceeded. Please wait a moment and try again."
        elif '401' in error_str or 'unauthorized' in error_str.lower():
            user_message = "API authentication failed. Please check your API key."
        else:
            user_message = f"Error processing message: {error_str[:200]}"
        
        return JsonResponse({
            'error': user_message,
            'status': 'error'
        }, status=500)
