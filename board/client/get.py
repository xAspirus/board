import lorem  # type: ignore
from scratchclient import ScratchSession  # type: ignore


sess = ScratchSession("aspirus", open("/home/aspirus/e").read().strip())
for follower in sess.get_user("kouzone").get_followers(limit=20):
    print(
        f"""
<div class="post">
<div class="info">
<a href="/u/{follower.username}" class="user">{follower.username}</a><span class="date">MM:HH DD/MM/YY</span><div class="right"><a href="">delete</a><a href="">quote</a></div>
</div>
<div class="content">{lorem.paragraph()}</div>
</div>
"""[1:])
