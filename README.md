# ndb-faker

NDB Model &amp; Properties for creating entities with fake data.

#
## Introduction -- nix?

NDB Faker provides a convenient way to test and prototype your GAE applications with fake data by providing
a simple wrapper around the Faker library.

#
## Installing

Include the `ndb_faker` folder in your app 'libs' folder, or wherever you keep your third-party libraries,
along with the 'faker' module that it's dependent on.

> Since the faker repo is included as a `git submodule` you will need to extract and replace the
outer `faker` folder with the inner `faker` module.

#
## Dependencies

* [NDB](https://developers.google.com/appengine/docs/python/ndb/)
* [Faker](https://github.com/deepthawtz/faker)

#
## Usage

Using `ndb_faker` is pretty straightforward.

Instead of:

```python

from google.appengine.ext import ndb

class MyModel(ndb.Model):
    name = ndb.StringProperty()
    ...

```

You import `ndb_faker` instead and use its Model and Properties:

```python

import ndb_faker

class MyModel(ndb_faker.Model):
    name = ndb_faker.StringProperty()
    ...

```

If you prefer you can also:

```python

from ndb_faker import model

class MyModel(model.Model):
    name = model.StringProperty()
    ...

```

Or even:

```python

from ndb_faker import fake

class MyModel(fake.Model):
    name = fake.StringProperty()
    ...

```


















#
## License

This package is offered under the MIT License, see `LICENSE` for more details.








































