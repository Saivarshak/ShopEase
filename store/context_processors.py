def user_profile(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {
            'profile_photo_url': '',
            'profile_display_text': '',
            'profile_initial': '',
        }

    email_or_username = user.email or user.username or ''

    # Priority 1: Session-stored profile photo URL (set after Google login).
    # A fallback from an earlier login must not prevent a later Google photo
    # lookup after the OAuth pipeline has been updated.
    profile_photo_url = request.session.get('profile_photo_url', '')
    if profile_photo_url.startswith('https://ui-avatars.com/api/'):
        profile_photo_url = ''
        request.session.pop('profile_photo_url', None)
        request.session.modified = True

    # Priority 2: Try to get the Google photo from all social-auth fields.

    if not profile_photo_url:
        try:
            from social_django.models import UserSocialAuth
            from .views import _extract_profile_photo_url
            social = UserSocialAuth.objects.filter(user=user, provider='google-oauth2').first()
            if social and social.extra_data:
                profile_photo_url = _extract_profile_photo_url(social.extra_data)
                if profile_photo_url:
                    request.session['profile_photo_url'] = profile_photo_url
                    request.session.modified = True
        except Exception:
            pass

    # Priority 3: UI Avatars fallback based on user's name/email
    if not profile_photo_url:
        import urllib.parse
        display_name = user.get_full_name() or email_or_username
        ui_avatar_url = f"https://ui-avatars.com/api/?name={urllib.parse.quote(display_name)}&background=000000&color=ffffff&size=128&font-size=0.45&rounded=true&bold=true"
        profile_photo_url = ui_avatar_url

    return {
        'profile_photo_url': profile_photo_url,
        'profile_display_text': email_or_username,
        'profile_initial': (email_or_username[:1] or '').upper(),
    }
