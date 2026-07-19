class DisabledProvider:
    name="disabled"; allowed_models=set()
    def submit(self, request): raise RuntimeError("cloud provider disabled")
