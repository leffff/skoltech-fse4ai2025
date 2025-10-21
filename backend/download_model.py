from transformers import BlipProcessor, BlipForConditionalGeneration

print("Pre-downloading BLIP model...")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
print("✅ BLIP model downloaded and cached.")