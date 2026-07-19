from hashlib import sha256
from .base import ProviderResult
class MockProvider:
    name="mock"; allowed_models={"mock-ocr-v1","mock-review-v1"}
    def submit(self, request):
        h="sha256:"+sha256(str(request).encode()).hexdigest()
        return ProviderResult(self.name,request.get("model","mock-review-v1"),h,{"state":"CANDIDATE","request_hash":h,"findings":[{"kind":"summary","text":"mock candidate"}],"authoritative_state_changes":[]},10,10,0.0)
