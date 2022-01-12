from core.application import create_app

app = create_app()

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000) pour passer sur le réseaux

    app.run(host='localhost', port=5000)
