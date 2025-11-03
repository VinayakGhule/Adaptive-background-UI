from django.shortcuts import render
from django.http import JsonResponse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import json

def index(request):
    typing_speed = None
    word_count = 0
    sentiment = None
    background = "linear-gradient(135deg, #92bfff 0%, #bc6ff1 100%)"  # Default neutral gradient
    
    if request.method == "POST":
        sid_obj = SentimentIntensityAnalyzer()
        # Get the textarea value and elapsed seconds from the POST data
        typed_text = request.POST.get("typed_text", "")
        sentiment_dict = sid_obj.polarity_scores(typed_text)
        elapsed_seconds = int(request.POST.get("elapsed_seconds", 0))
        word_count = len([w for w in typed_text.split() if w.strip()])
        # Only calculate and display typing speed after every 20s interval (20, 40, 60,...)
        if elapsed_seconds > 0 and elapsed_seconds % 20 == 0:
            wpm = (word_count / elapsed_seconds) * 60
            typing_speed = round(wpm, 2)
            if sentiment_dict['compound'] >= 0.05:
                sentiment = "Positive"
                # Peaceful positive gradient - multiple color stops for smoothness
                background = "linear-gradient(135deg, #a8e6cf 0%, #88d8c0 25%, #7fcdcd 50%, #6bb6ff 75%, #a8e6cf 100%)"
            elif sentiment_dict['compound'] <= -0.05:
                sentiment = "Negative"
                # Dark negative gradient - deep blues and dark purples with smooth transitions
                background = "linear-gradient(135deg, #2c3e50 0%, #34495e 25%, #2c3e50 50%, #1a252f 75%, #2c3e50 100%)"
            else:
                sentiment = "Neutral"
                # Enhanced neutral gradient with smooth transitions
                background = "linear-gradient(135deg, #92bfff 0%, #bc6ff1 25%, #92bfff 50%, #dda0dd 75%, #92bfff 100%)"
            
    # Always pass live word_count to template, display typing_speed only if calculated
    context = {"word_count": word_count, "sentiment": sentiment, "background": background}
    if typing_speed is not None:
        context["typing_speed"] = typing_speed
    return render(request, 'home/index.html', context)


def analyze_sentiment(request):
    """API endpoint for real-time sentiment analysis"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            
            if not text.strip():
                return JsonResponse({
                    'sentiment': 'neutral',
                    'polarity': 0.0,
                    'subjectivity': 0.0,
                    'scores': {
                        'positive': 0.0,
                        'negative': 0.0,
                        'neutral': 1.0,
                        'compound': 0.0
                    }
                })
            
            # VADER Sentiment Analysis
            sid_obj = SentimentIntensityAnalyzer()
            vader_scores = sid_obj.polarity_scores(text)
            
            # TextBlob Sentiment Analysis
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Determine overall sentiment
            if vader_scores['compound'] >= 0.05:
                overall_sentiment = 'positive'
            elif vader_scores['compound'] <= -0.05:
                overall_sentiment = 'negative'
            else:
                overall_sentiment = 'neutral'
            
            return JsonResponse({
                'sentiment': overall_sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'scores': vader_scores
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# Create your views here.
