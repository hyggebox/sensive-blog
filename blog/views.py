from django.shortcuts import render
from blog.models import Post, Tag
from django.db.models import Count, Prefetch


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.num_comments,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.ordered_tags],
        'first_tag_title': post.ordered_tags[0].title,
    }


def serialize_post_old(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.num_comments,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.popular()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.num_related_posts,
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


def index(request):
    most_popular_posts = Post.objects.popular().prefetch_related(
        Prefetch('author'),
        Prefetch('tags',
                 queryset=Tag.objects.popular(),
                 to_attr='ordered_tags'))[:5]
    fetch_with_comments_num(most_popular_posts)

    fresh_posts = Post.objects.prefetch_related(
        Prefetch('author'),
        Prefetch('tags',
                 queryset=Tag.objects.popular(),
                 to_attr='ordered_tags')).order_by('-published_at')[:5]
    fetch_with_comments_num(fresh_posts)

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
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

    related_tags = post.tags.all().popular()

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

    most_popular_posts = Post.objects.popular().prefetch_related(
        Prefetch('author'),
        Prefetch('tags', queryset=Tag.objects.popular(),
                 to_attr='ordered_tags'))[:5]
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

    most_popular_posts = Post.objects.popular().prefetch_related(
        Prefetch('author'),
        Prefetch('tags', queryset=Tag.objects.popular(),
                 to_attr='ordered_tags'))[:5]
    fetch_with_comments_num(most_popular_posts)

    related_posts = tag.posts.all().prefetch_related(
        Prefetch('author'),
        Prefetch('tags', queryset=Tag.objects.popular(),
                 to_attr='ordered_tags'))[:20]
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
