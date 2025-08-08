import os
import csv
import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import PostForm, CommentForm
import base64
from bs4 import BeautifulSoup
import time
import re

# Cricket news API
def fetch_cricket_news():
    api_key = '69c489f3a8e246d49326d3b08725dea7'
    url = f'https://newsapi.org/v2/everything?q=cricket&language=en&sortBy=publishedAt&apiKey={api_key}'
    
    try:
        response = requests.get(url)
        data = response.json()
        return data['articles'][:5]  # Limit to 5 news items
    except:
        return []

# Function to scrape full article content using BeautifulSoup only
def scrape_full_article(url):
    """
    Scrape the full article content from the given URL using BeautifulSoup
    Returns a dictionary with full_content and success status
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        unwanted_tags = [
            'script', 'style', 'nav', 'header', 'footer', 'aside', 
            'advertisement', 'ads', 'social-share', 'related-articles',
            'comments', 'sidebar', 'menu', 'breadcrumb', 'pagination'
        ]
        
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove elements by class names that are commonly ads/navigation
        unwanted_classes = [
            'ad', 'ads', 'advertisement', 'social', 'share', 'related',
            'sidebar', 'navigation', 'nav', 'menu', 'header', 'footer',
            'comment', 'breadcrumb', 'pagination', 'tag', 'category'
        ]
        
        for class_name in unwanted_classes:
            for element in soup.find_all(class_=re.compile(class_name, re.I)):
                element.decompose()
        
        # Try different selectors commonly used for article content
        content_selectors = [
            # Specific article selectors
            'article[role="main"]',
            'article.post-content',
            'article.entry-content',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content-body',
            '.story-body',
            '.article-body',
            '.main-content',
            '.post-body',
            
            # Generic content selectors
            '[data-module="ArticleBody"]',
            '[data-component="ArticleBody"]', 
            '.field-name-body',
            '.node-content',
            '.content',
            '#content',
            '.text-content',
            '.article-text',
            
            # Fallback to article tag
            'article',
            'main',
        ]
        
        full_content = ""
        successful_selector = None
        
        for selector in content_selectors:
            try:
                content_div = soup.select_one(selector)
                if content_div:
                    # Extract text from paragraphs and headings
                    content_elements = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div'])
                    content_parts = []
                    
                    for element in content_elements:
                        text = element.get_text().strip()
                        # Filter out very short snippets, navigation text, etc.
                        if (text and 
                            len(text) > 30 and  # Minimum length
                            not re.match(r'^(share|follow|subscribe|read more|continue reading|advertisement)', text.lower()) and
                            not re.search(r'^(tags?|categories?|related|more from)', text.lower()) and
                            len(text.split()) > 5):  # At least 5 words
                            content_parts.append(text)
                    
                    if content_parts and len(content_parts) >= 2:  # Need at least 2 substantial paragraphs
                        full_content = '\n\n'.join(content_parts)
                        successful_selector = selector
                        break
            except Exception as e:
                continue
        
        # If no specific content div found, try to get all paragraphs from body
        if not full_content:
            body = soup.find('body')
            if body:
                paragraphs = body.find_all('p')
                content_parts = []
                
                for para in paragraphs:
                    text = para.get_text().strip()
                    # More strict filtering for body-wide paragraph extraction
                    if (text and 
                        len(text) > 50 and  # Longer minimum for body extraction
                        not re.search(r'(cookie|privacy|subscribe|newsletter|follow|share|comment|advertisement)', text.lower()) and
                        len(text.split()) > 8):  # At least 8 words
                        content_parts.append(text)
                
                if content_parts and len(content_parts) >= 3:  # Need at least 3 paragraphs from body
                    full_content = '\n\n'.join(content_parts[:10])  # Limit to first 10 paragraphs
                    successful_selector = 'body paragraphs'
        
        # Clean up the content
        if full_content:
            # Remove excessive whitespace
            full_content = re.sub(r'\n\s*\n\s*\n', '\n\n', full_content)
            full_content = re.sub(r' {2,}', ' ', full_content)
            
            # Check if we have substantial content
            if len(full_content.strip()) > 200:  # At least 200 characters
                return {
                    'success': True,
                    'full_content': full_content.strip(),
                    'method': f'beautifulsoup ({successful_selector})',
                    'word_count': len(full_content.split())
                }
        
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'full_content': None,
            'method': None,
            'error': 'Request timeout'
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'full_content': None,
            'method': None,
            'error': f'Request failed: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'full_content': None,
            'method': None,
            'error': f'Parsing failed: {str(e)}'
        }
    
    return {
        'success': False,
        'full_content': None,
        'method': None,
        'error': 'No substantial content found'
    }

# Home page with posts, comments, and news headlines only
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    news_articles = fetch_cricket_news()

    if request.method == 'POST' and 'submit_comment' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            post_id = request.POST.get('post_id')
            post = get_object_or_404(Post, id=post_id)
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('home')
    else:
        comment_form = CommentForm()

    context = {
        'comment_form': comment_form,
        'posts': posts,
        'news_articles': news_articles,
    }
    return render(request, 'home.html', context)

# News detail view using Base64-encoded URL with full article scraping
def news_detail(request):
    encoded_url = request.GET.get('url', '')
    if not encoded_url:
        return render(request, 'news_detail.html', {'error': 'No URL provided'})
    
    try:
        decoded_url = base64.urlsafe_b64decode(encoded_url + '===').decode('utf-8')
        news_articles = fetch_cricket_news()
        article = next((a for a in news_articles if a['url'] == decoded_url), None)
        
        if not article:
            return render(request, 'news_detail.html', {'error': 'Article not found'})
        
        # Scrape the full article content
        print(f"Attempting to scrape: {decoded_url}")  # Debug log
        scraping_result = scrape_full_article(decoded_url)
        
        if scraping_result['success']:
            # Add the scraped content to the article data
            article['full_content'] = scraping_result['full_content']
            article['scraping_method'] = scraping_result['method']
            article['word_count'] = scraping_result.get('word_count', 0)
            print(f"Successfully scraped {article['word_count']} words")  # Debug log
        else:
            # Fallback to the original content snippet
            article['full_content'] = article.get('content', 'Content not available.')
            article['scraping_method'] = None
            article['scraping_error'] = scraping_result.get('error', 'Unknown error')
            print(f"Scraping failed: {scraping_result.get('error', 'Unknown error')}")  # Debug log
        
        return render(request, 'news_detail.html', {'article': article})
        
    except (base64.binascii.Error, UnicodeDecodeError):
        return render(request, 'news_detail.html', {'error': 'Invalid URL'})
    except Exception as e:
        print(f"Error in news_detail view: {e}")
        return render(request, 'news_detail.html', {'error': 'Failed to load article'})

# Community page with post and comment functionality
@login_required
def posts(request):
    posts = Post.objects.all().order_by('-created_at')

    if request.method == 'POST':
        if 'submit_post' in request.POST:
            post_form = PostForm(request.POST, request.FILES)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.user = request.user
                post.save()
                return redirect('community')
        elif 'submit_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                post_id = request.POST.get('post_id')
                post = get_object_or_404(Post, id=post_id)
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.save()
                return redirect('community')
    else:
        post_form = PostForm()
        comment_form = CommentForm()

    context = {
        'post_form': post_form,
        'comment_form': comment_form,
        'posts': posts,
    }
    return render(request, 'posts.html', context)

# DELETE POST view
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user:
        post.delete()
    return redirect('community')

# Player statistics view
def player_stats(request):
    players = []
    csv_path = os.path.join(settings.BASE_DIR, 'data', 'players.csv')

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            players.append(row)

    selected_format = request.POST.get('format') if request.method == 'POST' else 'All'
    selected_name = request.POST.get('player_name') if request.method == 'POST' else None
    selected_player = None
    image_url = None

    if selected_name:
        for player in players:
            if player['name'] == selected_name and (selected_format == 'All' or player['format'] == selected_format):
                selected_player = player
                image_filename = selected_name.lower().replace(" ", "_") + ".jpg"
                image_url = f"images/players/{image_filename}"
                break

    player_names = sorted(set(p['name'] for p in players))
    formats = ["All", "Test", "ODI", "T20I"]

    context = {
        'players': player_names,
        'formats': formats,
        'selected_player': selected_player,
        'selected_format': selected_format,
        'image_url': image_url
    }
    return render(request, 'player_stats.html', context)

# Player comparison view
def player_comparison(request):
    players = []
    csv_path = os.path.join(settings.BASE_DIR, 'data', 'players.csv')

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            players.append(row)

    selected_format = request.POST.get('format') if request.method == 'POST' else 'All'
    name1 = request.POST.get('player1') if request.method == 'POST' else None
    name2 = request.POST.get('player2') if request.method == 'POST' else None

    p1 = p2 = None
    image_url1 = image_url2 = None

    if name1:
        for player in players:
            if player['name'] == name1 and (selected_format == 'All' or player['format'] == selected_format):
                p1 = player
                image_filename1 = name1.lower().replace(" ", "_") + ".jpg"
                image_url1 = f"images/players/{image_filename1}"
                break

    if name2:
        for player in players:
            if player['name'] == name2 and (selected_format == 'All' or player['format'] == selected_format):
                p2 = player
                image_filename2 = name2.lower().replace(" ", "_") + ".jpg"
                image_url2 = f"images/players/{image_filename2}"
                break

    player_names = sorted(set(p['name'] for p in players))
    formats = ["All", "Test", "ODI", "T20I"]

    selected_players = []
    if p1:
        selected_players.append((p1, image_url1))
    if p2:
        selected_players.append((p2, image_url2))

    context = {
        'selected_players': selected_players,
        'player_names': player_names,
        'formats': formats,
        'selected_format': selected_format,
    }
    return render(request, 'player_comparison.html', context)

# Match prediction logic
def match_prediction(request):
    teams = []
    venues = []
    prediction = None

    match_data_path = os.path.join(settings.BASE_DIR, 'data', 'match_data.csv')
    with open(match_data_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        match_data = list(reader)
        teams = sorted(set(row['team1'] for row in match_data).union(set(row['team2'] for row in match_data)))
        venues = sorted(set(row['venue'] for row in match_data))

    if request.method == 'POST':
        team1 = request.POST.get('team1')
        team2 = request.POST.get('team2')
        venue = request.POST.get('venue')
        toss = request.POST.get('toss')
        decision = request.POST.get('decision')

        team1_wins = 0
        team2_wins = 0

        for row in match_data:
            if row['venue'] == venue:
                if row['winner'] == team1:
                    team1_wins += 1
                elif row['winner'] == team2:
                    team2_wins += 1

        if toss == team1 and decision == 'bat':
            team1_wins += 1
        elif toss == team2 and decision == 'bat':
            team2_wins += 1

        prediction = team1 if team1_wins >= team2_wins else team2

    context = {
        'teams': teams,
        'venues': venues,
        'prediction': prediction
    }
    return render(request, 'prediction.html', context)

# Like post view
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.likes += 1
    post.save()
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    if 'community' in referer:
        return redirect('community')
    return redirect('home')