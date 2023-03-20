from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Forum, Thread, Post
from users.models import User
from studyrooms.models import Studyroom
from .forms import ThreadForm, PostForm


@login_required()
def forum(request, forum_id):
    user = request.user
    forum = get_object_or_404(Forum, pk=forum_id)
    studyroom = forum.studyroom
    if not user in studyroom.member.all():
        return redirect("studyroom", studyroom.pk)

    if request.method == "GET":
        raw_threads = Thread.objects.filter(forum=forum)
        page = request.GET.get("page")
        paginator = Paginator(raw_threads, 10)
        threads = paginator.get_page(page)
        context = {
            "studyroomId": studyroom.pk,
            "studyroomName": studyroom.name,
            "isLeader": user == studyroom.leader,
            "forum": forum,
            "threads": threads,
            "forums": studyroom.forum_set.all(),
        }
        return render(request, "forum/studyroomForum.html", context)


@login_required()
def create_thread(request, forum_id):
    user = request.user
    forum = get_object_or_404(Forum, pk=forum_id)
    studyroom = forum.studyroom
    if not user in studyroom.member.all():
        return redirect("studyroom", studyroom.pk)
    context = {
        "studyroomId": studyroom.pk,
        "forumId": forum_id,
        "isLeader": user == studyroom.leader,
    }
    if request.method == "GET":
        return render(request, "forum/createThread.html", context)

    elif request.method == "POST":
        form = ThreadForm(request.POST)
        if form.is_valid():
            title_input = form.cleaned_data["title"]
            thread = Thread.objects.create(forum=forum, title=title_input, author=user)
            return redirect("thread", thread.pk)
        context["error"] = form.errors
        return render(request, "forum/createThread.html", context)


@login_required()
def thread(request, thread_id):
    user = request.user
    thread = get_object_or_404(Thread, pk=thread_id)
    forum = thread.forum
    studyroom = forum.studyroom
    if not user in studyroom.member.all():
        return redirect("studyroom", studyroom.pk)

    thread.last_update = thread.last_update.strftime("%Y-%m-%d %H:%M")
    raw_posts = thread.post_set.filter(is_deleted=False)
    posts = list()
    for raw_post in raw_posts:
        posts.append(
            {
                "id": raw_post.pk,
                "content": raw_post.content,
                "create_date": raw_post.create_date.strftime("%Y-%m-%d %H:%M"),
                "author": "익명" if raw_post.is_anonymous else raw_post.author,
                "is_author": user == raw_post.author,
            }
        )

    context = {
        "studyroomId": studyroom.pk,
        "forumId": forum.id,
        "isLeader": user == studyroom.leader,
        "thread": thread,
        "posts": posts,
    }

    if request.method == "GET":
        return render(request, "forum/thread.html", context)

    elif request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            content_input = form.cleaned_data["content"]
            is_anonymous_input = form.cleaned_data["is_anonymous"]
            post = Post.objects.create(
                thread=thread,
                content=content_input,
                author=user,
                is_anonymous=is_anonymous_input,
            )
            thread.last_update = post.create_date
            thread.save()
            return redirect("thread", thread.pk)
        context["error"] = form.errors
        return render(request, "forum/thread.html", context)


def delete_thread(request, thread_id):
    user = request.user
    thread = get_object_or_404(Thread, pk=thread_id)
    forum = thread.forum
    studyroom = forum.studyroom
    if not user in studyroom.member.all():
        return redirect("studyroom", studyroom.pk)

    if request.method == "GET":
        pass


def delete_post(request, thread_id, post_id):
    user = request.user
    post = get_object_or_404(Post, pk=post_id)
    thread = post.thread

    if request.method == "GET":
        if user == post.author:
            post.is_deleted = True
            post.save()
    return redirect("thread", thread.pk)


def postsearaaaaaaaaach(request, room_id, board_thema):
    if request.method == "GET":
        searchWord = request.GET.get("searchWord")
        print(searchWord)
        if request.GET["selectTag"] == "title":
            searchposts = Post.objects.filter(title__icontains=searchWord)
        elif request.GET["selectTag"] == "content":
            searchposts = Post.objects.filter(content__icontains=searchWord)
        elif request.GET["selectTag"] == "author":
            users = User.objects.filter(username__icontains=searchWord)
            count = 0
            for user in users:
                if count == 0:
                    searchposts = Post.objects.filter(author=user)
                    count += 1
                else:
                    searchposts = searchposts | Post.objects.filter(author=user)

        paginator = Paginator(searchposts, 5)
        page = request.GET.get("page")
        page_posts = paginator.get_page(page)

        if board_thema == "n":
            thema = "공지게시판"
        if board_thema == "f":
            thema = "자유게시판"
        if board_thema == "q":
            thema = "질문게시판"
        if board_thema == "i":
            thema = "정보게시판"
        context = {
            "room_id": room_id,
            "posts": searchposts,
            "board_thema": board_thema,
            "page_posts": page_posts,
            "thema": thema,
        }
    return render(request, "boards/boardlist.html", context)
