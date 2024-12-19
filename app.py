from app import create_app

# Run the App
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
