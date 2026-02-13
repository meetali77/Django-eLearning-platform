# from channels.generic.websocket import AsyncJsonWebsocketConsumer
# from django.contrib.auth.models import AnonymousUser
# from asgiref.sync import sync_to_async
# from .models import Course, Enrollment

# class CourseChatConsumer(AsyncJsonWebsocketConsumer):
#     async def connect(self):
#         self.course_id = self.scope["url_route"]["kwargs"]["course_id"]
#         self.group_name = f"course_{self.course_id}"

#         user = self.scope["user"]
#         if isinstance(user, AnonymousUser) or not await self._can_join(user.id, self.course_id):
#             await self.close()
#             return

#         await self.channel_layer.group_add(self.group_name, self.channel_name)
#         await self.accept()
#         await self.channel_layer.group_send(self.group_name, {
#             "type": "chat.system",
#             "message": f"{user.username} joined the chat."
#         })

#     async def disconnect(self, code):
#         await self.channel_layer.group_discard(self.group_name, self.channel_name)

#     async def receive_json(self, content, **kwargs):
#         user = self.scope["user"]
#         msg = content.get("message", "").strip()
#         if not msg:
#             return
#         await self.channel_layer.group_send(self.group_name, {
#             "type": "chat.message",
#             "username": user.username,
#             "message": msg
#         })

#     async def chat_message(self, event):
#         # broadcast user messages
#         await self.send_json({"type": "message", "user": event["username"], "text": event["message"]})

#     async def chat_system(self, event):
#         # broadcast system messages
#         await self.send_json({"type": "system", "text": event["message"]})

#     @sync_to_async
#     def _can_join(self, user_id, course_id):
#         try:
#             course = Course.objects.get(id=course_id)
#         except Course.DoesNotExist:
#             return False
#         # teacher of course OR enrolled student
#         if course.teacher_id == user_id:
#             return True
#         return Enrollment.objects.filter(course_id=course_id, student_id=user_id).exists()


from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Enrollment, Course

class CourseChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.course_id = int(self.scope["url_route"]["kwargs"]["course_id"])
        self.group_name = f"course_{self.course_id}"
        user = self.scope.get("user", AnonymousUser())

        # 401 if not signed in
        if not user.is_authenticated:
            await self.close(code=4401)
            return

        # 404 if course doesn't exist
        if not await self._course_exists(self.course_id):
            await self.close(code=4404)
            return

        # allow teacher, or enrolled student
        if not await self._has_access(user.id, getattr(user, "is_teacher", False), self.course_id):
            await self.close(code=4403)  # forbidden
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "chat.system", "text": f"{user.username} joined the chat."}
        )

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        msg_type = content.get("type")
        text = content.get("text")
        if text is None and "message" in content:
            msg_type = "message"
            text = content.get("message")

        text = (text or "").strip()
        if msg_type == "message" and text:
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "chat.message", "user": self.scope["user"].username, "text": text}
            )

    async def chat_message(self, event):
        await self.send_json({"type": "message", "user": event["user"], "text": event["text"]})

    async def chat_system(self, event):
        await self.send_json({"type": "system", "text": event["text"]})


    @database_sync_to_async
    def _course_exists(self, course_id: int) -> bool:
        return Course.objects.filter(id=course_id).exists()

    @database_sync_to_async
    def _has_access(self, user_id: int, is_teacher: bool, course_id: int) -> bool:
        if is_teacher:
            return True
        return Enrollment.objects.filter(course_id=course_id, student_id=user_id).exists()



