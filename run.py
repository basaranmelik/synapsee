from app import create_app


app = create_app()

if __name__ in "__main__":
    app.run(debug=True)