from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Count, Prefetch



def serialize_post_optimized(post):
    tags = post.tags.all()
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag_optimized(tag) for tag in tags],
        'first_tag_title': tags[0].title if tags else '',
    }


def serialize_tag_optimized(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def get_tags_prefetch():
    return Prefetch(
        'tags',
        queryset=Tag.objects.annotate(posts_count=Count('posts'))
    )

def get_most_popular_posts():
    return Post.objects.popular() \
        .fetch_with_comments_count() \
        .prefetch_related('author') \
        .prefetch_related(get_tags_prefetch())[:5]


def index(request):
    tags_prefetch = get_tags_prefetch()

    most_popular_posts = Post.objects.popular() \
        .fetch_with_comments_count() \
        .prefetch_related('author') \
        .prefetch_related(tags_prefetch)[:5]

    most_fresh_posts = Post.objects \
        .fetch_with_comments_count() \
        .prefetch_related('author') \
        .prefetch_related(tags_prefetch) \
        .order_by('-published_at')[:5]

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
        'page_posts': [
            serialize_post_optimized(post) for post in most_fresh_posts
        ],
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.annotate(
        likes_count=Count('likes')
    ).prefetch_related(
        get_tags_prefetch(), 'author'
    ).get(slug=slug)

    comments = Comment.objects.filter(post=post).select_related('author')
    serialized_comments = [
        {
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        }
        for comment in comments
    ]

    related_tags = post.tags.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag_optimized(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5]
    most_popular_posts = get_most_popular_posts()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = get_most_popular_posts()

    related_posts = tag.posts \
        .fetch_with_comments_count() \
        .prefetch_related('author', get_tags_prefetch()) \
        .all()[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
        'posts': [serialize_post_optimized(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})