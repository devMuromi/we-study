from django.shortcuts import get_object_or_404, render, redirect
from .models import Forum, Thread, Post
from users.models import User
from studyrooms.models import Studyroom
from .forms import ThreadForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


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
    if request.method == "GET":
        context = {
            "studyroomId": studyroom.pk,
            "forumId": forum.id,
            "isLeader": user == studyroom.leader,
            "thread": thread,
            "posts": thread.post_set.all(),
        }
        return render(request, "forum/thread.html", context)


def delete_thread(request, thread_id):
    pass


def delete_post(request, thread_id, post_id):
    pass


def post(request, studyroom_id, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        comment = Comment()
        comment.author = request.user
        comment.content = request.POST["content"]
        post = get_object_or_404(Post, pk=post_id)
        comment.board = post
        comment.save()
    comments = Comment.objects.filter(board=post)
    context = {
        "post": post,
        "comments": comments,
        "room_id": room_id,
    }
    return render(request, "boards/post.html", context)


def create_post(request, forum_type, studyroom_id):
    if request.method == "POST":
        post = Post()
        post.title = request.POST["title"]
        post.content = request.POST["content"]
        post.thema = board_thema
        post.author = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)
        post.studyroom = studyroom
        post.save()
        context = {
            "room_id": room_id,
            "board_thema": board_thema,
        }
        return redirect("/boards/board/" + board_thema + "/" + str(room_id))
    context = {
        "room_id": room_id,
        "board_thema": board_thema,
    }
    return render(request, "forum/createpost.html", context)


def edit_post(request, studyroom_id, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author == request.user:
        return render(
            request, "boards/postedit.html", {"post": post, "room_id": room_id}
        )
    else:
        message = "수정 권한이 없습니다."
        comments = Comment.objects.filter(board=post)
        context = {
            "post": post,
            "comments": comments,
            "message": message,
            "room_id": room_id,
        }
        return redirect("detail", room_id, post_id)


# def delete_post(request, studyroom_id, post_id):
#     deletepost = get_object_or_404(Post, pk=post_id)
#     if deletepost.author == request.user:
#         board_thema = deletepost.thema
#         room_id = deletepost.studyroom.id
#         deletepost.delete()
#         return redirect("/boards/board/" + board_thema + "/" + str(room_id))
#     else:
#         # messages.info(request, '삭제 권한이 없습니다')
#         # return redirect('/boards/detail/'+str(post_id))
#         message = "삭제 권한이 없습니다."
#         comments = Comment.objects.filter(board=deletepost)
#         context = {"message": message, "post": deletepost, "comments": comments}
#         # return redirect('/boards/board/'+board_thema+'/'+str(room_id))
#         return render(request, "boards/detail.html", context)


def update_post(request, studyroom_id, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, pk=post_id)
        post.title = request.POST["title"]
        post.content = request.POST["content"]
        post.save()
    return redirect("detail", room_id, post_id)


def postsearch(request, room_id, board_thema):
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


def commentdelete(request, room_id, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.delete()
    context = {"room_id": room_id}
    return redirect("detail", room_id, post_id)
