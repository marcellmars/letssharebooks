from sanic import Sanic
from sanic.response import json
from sanic.views import HTTPMethodView

from playhouse.shortcuts import model_to_dict

from models import Library, Book, OBJ


app = Sanic('letssharebooks')


#
# Views
#


class BaseView(HTTPMethodView):

    async def get(self, request):
        '''
        Return all objects
        '''
        objects = await OBJ.execute(self.model.select())
        return json(({'id': i.id} for i in objects))

    async def post(self, request):
        '''
        Insert many objects
        '''
        try:
            data = request.json
        except Exception:
            return json({'error': 'invalid json'})

        if isinstance(data, dict):
            data = [data]

        successes, fails = 0, 0
        async with OBJ.atomic():
            for item in data:
                try:
                    obj = await OBJ.create(self.model, **item)
                except Exception as e:
                    print(e)
                    fails += 1
                else:
                    successes += 1
        return json({'successes': successes, 'fails': fails})


class LibrariesView(BaseView):

    model = Library

    async def get(self, request, presence=None):
        libraries = Library.select()
        if presence is not None:
            if presence not in ('on', 'off'):
                return json({'error': 'invalid presence'})
            else:
                libraries = libraries.where(Library.presence == presence)
        objects = await OBJ.execute(libraries)
        return json((model_to_dict(i) for i in objects))


class BooksView(BaseView):

    model = Book


#
#  Routes
#


app.add_route(LibrariesView.as_view(), '/libraries')
app.add_route(LibrariesView.as_view(), '/libraries/<presence>')

app.add_route(BooksView.as_view(), '/books')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
