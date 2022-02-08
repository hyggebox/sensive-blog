from django.shortcuts import render
from blog.models import Post, Tag
from django.db.models import Count


def serialize_post(post):
    fetch_with_posts_num(post.tags.all())
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.num_comments,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.num_posts,
    }


def serialize_tag_optimized(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.num_posts,
    }


def fetch_with_comments_num(posts):
    posts_ids = [post.id for post in posts]
    posts_with_comments = Post.objects.filter(
        id__in=posts_ids).annotate(
        num_comments=Count('comments'))
    ids_and_comments = posts_with_comments.values_list('id', 'num_comments')
    count_for_id = dict(ids_and_comments)
    for post in posts:
        post.num_comments = count_for_id[post.id]
    return posts


def fetch_with_posts_num(tags):
    tags_ids = [tag.id for tag in tags]
    tags_with_posts = Tag.objects.filter(
        id__in=tags_ids).annotate(
        num_posts=Count('posts'))
    ids_and_posts = tags_with_posts.values_list('id', 'num_posts')
    count_for_id = dict(ids_and_posts)
    for tag in tags:
        tag.num_posts = count_for_id[tag.id]
    return tags


def index(request):
    most_popular_posts = Post.objects.popular()\
                             .prefetch_related('author', 'tags')[:5]
    fetch_with_comments_num(most_popular_posts)

    fresh_posts = Post.objects.prefetch_related('author', 'tags')\
                      .order_by('-published_at')[:5]
    fetch_with_comments_num(fresh_posts)

    most_popular_tags = Tag.objects.popular()[:5]
    fetch_with_posts_num(most_popular_tags)

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in fresh_posts],
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    comments = post.comments.all()
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.all()

    related_tags = post.tags.all()
    fetch_with_posts_num(related_tags)

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': len(likes),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5]
    fetch_with_posts_num(most_popular_tags)

    most_popular_posts = Post.objects.popular()\
                             .prefetch_related('author', 'tags')[:5]
    fetch_with_comments_num(most_popular_posts)

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]
    fetch_with_posts_num(most_popular_tags)

    most_popular_posts = Post.objects.popular()\
                             .prefetch_related('author', 'tags')[:5]
    fetch_with_comments_num(most_popular_posts)

    related_posts = tag.posts.all().prefetch_related('author', 'tags')[:20]
    fetch_with_comments_num(related_posts)

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
