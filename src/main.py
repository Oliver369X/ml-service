"""
ML Service Main Application
FastAPI + Strawberry GraphQL
"""
from fastapi import FastAPI, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from typing import Optional
from sqlalchemy.orm import Session

from .graphql import schema
from .graphql.context import Context
from .database import get_db, init_db
from .config import get_settings
from .utils.logger import logger

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="ML/DL Service",
    description="Machine Learning and Deep Learning Microservice for Personal Finance",
    version=settings.ml_model_version
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom context getter for GraphQL
async def get_context(
    db: Session = Depends(get_db),
    userid: Optional[str] = Header(None, alias="userid"),
    user_id: Optional[str] = Header(None, alias="user-id"),
    permissions: Optional[str] = Header(None)
) -> Context:
    """
    Create GraphQL context from headers
    
    The gateway sends userId and permissions in headers after validating JWT.
    We trust the gateway and don't re-validate JWT here.
    """
    # Get user ID (try both header formats)
    uid = userid or user_id
    
    logger.debug(f"GraphQL request - User ID: {uid}, Permissions: {permissions}")
    
    return Context(
        db=db,
        user_id=uid,
        permissions=permissions
    )


# GraphQL router
graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphiql=settings.env == "development"
)

# Mount GraphQL endpoint
app.include_router(graphql_router, prefix="/graphql")


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup"""
    logger.info("Starting ML Service...")
    logger.info(f"Environment: {settings.env}")
    logger.info(f"Model version: {settings.ml_model_version}")
    
    # Initialize database (create tables if they don't exist)
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down ML Service...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ML/DL Service",
        "version": settings.ml_model_version,
        "status": "running",
        "endpoints": {
            "graphql": "/graphql",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from .database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "database": db_status,
        "service": "ml-service",
        "version": settings.ml_model_version
    }


@app.get("/models/status")
async def models_status():
    """Check ML models status"""
    from .ml import TransactionClassifier, ExpenseForecaster
    from .dl import PatternAnalyzer
    
    classifier = TransactionClassifier()
    forecaster = ExpenseForecaster()
    pattern_analyzer = PatternAnalyzer()
    
    return {
        "classifier": {
            "loaded": classifier.is_trained,
            "path": settings.classifier_model_path
        },
        "forecaster": {
            "loaded": forecaster.is_trained,
            "path": settings.forecaster_model_path
        },
        "pattern_analyzer": {
            "loaded": pattern_analyzer.is_trained,
            "path": settings.pattern_model_path
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.env == "development"
    )

