import tempfile
from django.urls import reverse
from django.conf import settings

USERNAME = 'NoName'
USERNAME_2 = 'NoName_2'
SLUG = 'test-slug'
INDEX = reverse("posts:index")
GROUP_LIST = reverse("posts:group_list", args=[SLUG])
PROFILE = reverse("posts:profile", args=[USERNAME])
PROFILE_2 = reverse("posts:profile", args=[USERNAME_2])
POST_CREATE = reverse("posts:post_create")
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )