from typing import Dict, Any, List, Union
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from transformers import pipeline
import torch
from PIL import Image
import io
from core import BaseAgent, AgentConfig
from rich.console import Console

class AnalysisAgent(BaseAgent):
    """Agent for advanced analysis using ML/AI"""
    
    def _initialize(self) -> None:
        self.console = Console()
        self._load_models()
        self.supported_tasks = [
            "text_classification",
            "sentiment_analysis",
            "image_classification",
            "text_clustering",
            "summarization"
        ]
    
    def _load_models(self) -> None:
        """Load ML models and pipelines"""
        # Initialize models lazily to save memory
        self.models: Dict[str, Any] = {}
        
        # Text clustering setup
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.clusterer = KMeans(n_clusters=3)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data using various ML/AI techniques"""
        task = input_data.get("task", "")
        data = input_data.get("data", "")
        options = input_data.get("options", {})
        
        if task not in self.supported_tasks:
            raise ValueError(f"Unsupported task: {task}")
        
        if task == "text_classification":
            return await self._classify_text(data, options)
        elif task == "sentiment_analysis":
            return await self._analyze_sentiment(data, options)
        elif task == "image_classification":
            return await self._classify_image(data, options)
        elif task == "text_clustering":
            return await self._cluster_text(data, options)
        elif task == "summarization":
            return await self._summarize_text(data, options)
        
        return {"error": "Task not implemented"}
    
    async def _classify_text(
        self,
        text: Union[str, List[str]],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classify text using transformer models"""
        try:
            if "text_classification" not in self.models:
                self.models["text_classification"] = pipeline(
                    "text-classification",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
            
            result = self.models["text_classification"](text)
            return {"classification": result}
            
        except Exception as e:
            await self.handle_error(e)
            return {"error": str(e)}
    
    async def _analyze_sentiment(
        self,
        text: Union[str, List[str]],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze sentiment in text"""
        try:
            if "sentiment" not in self.models:
                self.models["sentiment"] = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
            
            result = self.models["sentiment"](text)
            return {"sentiment": result}
            
        except Exception as e:
            await self.handle_error(e)
            return {"error": str(e)}
    
    async def _classify_image(
        self,
        image_data: Union[str, bytes],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classify images using vision models"""
        try:
            if "image_classification" not in self.models:
                self.models["image_classification"] = pipeline(
                    "image-classification",
                    model="google/vit-base-patch16-224"
                )
            
            # Handle both file paths and raw bytes
            if isinstance(image_data, str):
                image = Image.open(image_data)
            else:
                image = Image.open(io.BytesIO(image_data))
            
            result = self.models["image_classification"](image)
            return {"classification": result}
            
        except Exception as e:
            await self.handle_error(e)
            return {"error": str(e)}
    
    async def _cluster_text(
        self,
        texts: List[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cluster text documents"""
        try:
            # Vectorize texts
            vectors = self.vectorizer.fit_transform(texts)
            
            # Perform clustering
            clusters = self.clusterer.fit_predict(vectors)
            
            # Get cluster centers
            centers = self.clusterer.cluster_centers_
            
            # Get top terms per cluster
            feature_names = self.vectorizer.get_feature_names_out()
            top_terms = []
            
            for center in centers:
                top_indices = np.argsort(center)[-5:][::-1]
                top_terms.append([feature_names[i] for i in top_indices])
            
            return {
                "clusters": clusters.tolist(),
                "top_terms_per_cluster": top_terms
            }
            
        except Exception as e:
            await self.handle_error(e)
            return {"error": str(e)}
    
    async def _summarize_text(
        self,
        text: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Summarize text using transformers"""
        try:
            if "summarization" not in self.models:
                self.models["summarization"] = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn"
                )
            
            result = self.models["summarization"](
                text,
                max_length=options.get("max_length", 130),
                min_length=options.get("min_length", 30),
                do_sample=False
            )
            
            return {"summary": result[0]["summary_text"]}
            
        except Exception as e:
            await self.handle_error(e)
            return {"error": str(e)}
    
    async def handle_error(self, error: Exception) -> None:
        """Handle analysis errors"""
        self.console.print(f"[red]Analysis error: {str(error)}[/red]")
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.supported_tasks
