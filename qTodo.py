from app import create_app, create_db_table

app = create_app()


if __name__ == '__main__':
    # create_db_table(app)
    app.run(debug=True)
