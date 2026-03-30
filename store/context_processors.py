def user_profile(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {
            'profile_photo_url': '',
            'profile_display_text': '',
            'profile_initial': '',
        }

    email_or_username = user.email or user.username or ''
    return {
        'profile_photo_url': request.session.get('profile_photo_url', ''),
        'profile_display_text': f"{email_or_username[:5]}..." if email_or_username else '',
        'profile_initial': (email_or_username[:1] or '').upper(),
    }
