import uvicorn
import sys
import logging

def main():
    try:
        uvicorn.run(
            "web.api:app",
            host="0.0.0.0",
            port=8088,  # Changed to 8088
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
