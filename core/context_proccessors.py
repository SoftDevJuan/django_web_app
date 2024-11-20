def usuario_y_grupo(request):
    if request.user.is_authenticated:
        usuario = request.user
        nombreGrupo = request.user.groups.first().name if request.user.groups.exists() else ''
    else:
        usuario = None
        nombreGrupo = ''

    return {
        'usuario': usuario,
        'nombreGrupo': nombreGrupo,
    }
