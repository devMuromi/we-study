from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from users.models import *
from studyrooms.models import *
from django.contrib import messages
from django.core.paginator import Paginator

# Create your views here.


def postedit(request, room_id, post_id):
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


def board(request, board_id, studyroom_id):
    studyroom = get_object_or_404(Studyroom, pk=studyroom_id)
    allposts = Post.objects.filter(studyroom=studyroom)
    posts = allposts.filter(thema=board_id)
    paginator = Paginator(posts, 5)
    page = request.GET.get("page")
    page_posts = paginator.get_page(page)

    if board_id == "n":
        thema = "공지게시판"
    if board_id == "f":
        thema = "자유게시판"
    if board_id == "q":
        thema = "질문게시판"
    if board_id == "i":
        thema = "정보게시판"

    context = {
        "room_id": studyroom_id,
        "posts": posts,
        "board_thema": board_id,
        "page_posts": page_posts,
        "thema": thema,
    }
    return render(request, "boards/boardlist.html", context)


def postnew(request, room_id, board_thema):
    context = {
        "room_id": room_id,
        "board_thema": board_thema,
    }
    return render(request, "boards/postnew.html", context)


def postcreate(request, room_id, board_thema):
    print(request.method)
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


def detail(request, room_id, post_id):
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
    return render(request, "boards/detail.html", context)


def postdelete(request, room_id, post_id):

    deletepost = get_object_or_404(Post, pk=post_id)
    if deletepost.author == request.user:
        board_thema = deletepost.thema
        room_id = deletepost.studyroom.id
        deletepost.delete()
        return redirect("/boards/board/" + board_thema + "/" + str(room_id))
    else:
        # messages.info(request, '삭제 권한이 없습니다')
        # return redirect('/boards/detail/'+str(post_id))
        message = "삭제 권한이 없습니다."
        comments = Comment.objects.filter(board=deletepost)
        context = {"message": message, "post": deletepost, "comments": comments}
        # return redirect('/boards/board/'+board_thema+'/'+str(room_id))
        return render(request, "boards/detail.html", context)


def postupdate(request, room_id, post_id):
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
