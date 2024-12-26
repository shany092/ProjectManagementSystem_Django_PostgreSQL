# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from .models import Employee

# @receiver(post_save, sender=Employee)
# def send_employee_creation_email(sender, instance, created, **kwargs):
#     if created:  # Only send email for new employees
#         password = instance.get_generated_password()  # Use the method to retrieve the password
#         send_mail(
#             subject='Welcome to Our System',
#             message=f'Your account has been created.\nUsername: {instance.user.username}\nPassword: {password}',
#             from_email='admin@example.com',
#             recipient_list=[instance.email],
#         )



# # # import random
# # # from django.contrib.auth.base_user import BaseUserManager
# # # from django.contrib.auth import get_user_model
# # # from django.db.models.signals import post_save, pre_save
# # # from django.dispatch import receiver
# # # from pmpapp.models import CustomUser, Employee
# # from django.contrib.auth.models import User
# # from django.contrib.auth.base_user import BaseUserManager  # Correct location for password generation
# # from django.db.models.signals import pre_save
# # from django.dispatch import receiver
# # from .models import Employee

# # @receiver(pre_save, sender=Employee)
# # def create_user_for_employee(sender, instance, **kwargs):
# #     if not instance.user_id:  # Check if the `user` field is not yet assigned
# #         username = f"employee_{instance.employee_code}"
# #         email = f"{username}@example.com"
# #         password = BaseUserManager().make_random_password()  # Corrected call to generate random password

# #         user = User.objects.create_user(
# #             username=username,
# #             email=email,
# #             password=password
# #         )
# #         instance.user = user
# #         # Optional: Log or store password securely
# #         print(f"Generated password for {user.username}: {password}")

# @receiver(pre_save, sender=CustomUser)
# def set_username(sender, instance, **kwargs):
#     if not instance.username:  # Only generate if the username is not set
#         while True:
#             random_number = random.randint(100, 999)
#             username = f"{instance.first_name}{instance.last_name}{random_number}".replace(" ", "")
#             if not CustomUser.objects.filter(username=username).exists():
#                 instance.username = username
#                 break
# @receiver(post_save, sender=Employee)
# def create_user_for_employee(sender, instance, created, **kwargs):
#     if created and not instance.user:
#         CustomUser = get_user_model()
#         user = CustomUser.objects.create(
#             first_name="Default",
#             last_name="Employee",
#             email=f"employee{instance.id}@example.com",
#             password=CustomUser.objects.make_random_password(),
#         )
#         instance.user = user
#         instance.save()
# @receiver(pre_save, sender=CustomUser)
# def set_password(sender, instance, **kwargs):
#     if not instance.password:  # Only generate if the password is not set
#         instance.set_password(BaseUserManager().make_random_password())

# @receiver(post_save, sender=CustomUser)
# def create_employee_profile(sender, instance, created, **kwargs):
#     if created:
#         Employee.objects.create(user=instance)