from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):
    def form_valid(self, form):
        remember_me = self.request.POST.get("remember_me")

        # Se "manter conectado" não for marcado, expira ao fechar o navegador
        if not remember_me:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(604800)  # 1 semana (em segundos)

        return super().form_valid(form)
