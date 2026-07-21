from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.image_processor import ImageProcessor
from app.services.inference_engine import InferenceEngine

app = FastAPI(title="Deepfake Image Validator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set use_mock=False to use the loaded PyTorch structural configurations
processor = ImageProcessor()
engine = InferenceEngine(use_mock=True)

@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid media type file layout extension.")
        
    try:
        contents = await file.read()
        original_img, processed_tensor, faces = processor.preprocess_face(contents)
        
        # Execute Pipeline Inference
        real_probability = engine.predict(processed_tensor)
        
        # Generate Heatmap Evaluation Overlays
        heatmap_url = processor.generate_heatmap(original_img, faces, real_probability)
        
        # Assign contextual threshold breakdowns
        if real_probability >= 0.85:
            verdict = "Highly Authentic"
            explanation = "No structural manipulation vectors or blending inconsistencies were recognized inside profile frames."
        elif real_probability >= 0.50:
            verdict = "Suspicious Modifications"
            explanation = "Minor frequency irregularities or computational edge variances detected. Potential low-level generative modification."
        else:
            verdict = "AI-Generated Alteration Detected"
            explanation = "High structural configuration dissonance identified. Generative facial mesh textures conflict with foundational surface rendering."

        return {
            "authenticityScore": int(real_probability * 100),
            "verdict": verdict,
            "explanation": explanation,
            "heatmapImage": heatmap_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Image Analysis Pipeline Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)