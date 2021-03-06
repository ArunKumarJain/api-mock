import json
import sys
sys.path.append(".")
from mockserver import MockServer, mockWrapper
import time

class ApiMock(MockServer):

    def __init__(self, host = "127.0.0.1", port = 5432):

        super(ApiMock, self).__init__(host = host, port = port)
        self.initialise()

    @mockWrapper
    def onMobileModelInfo(self, **kwargs):
        """
        callback function for the route GET: /mobiles/<manufacturer>/<model>
        """

        # example of how to read path segment parameter /mobiles/samsung/galaxy_a8
        priceJson = {"message": "unknown model"}
        # logic to return price based on manufacturer and model given
        if kwargs["manufacturer"].lower() == "samsung":
            if kwargs["model"].lower() == "galaxy_a8":
                priceJson = {"price": 52000}
            elif kwargs["model"].lower() == "galaxy_s9":
                priceJson = {"price": 54000}
        elif kwargs["manufacturer"].lower() == "apple":
            if kwargs["model"].lower() == "xs":
                priceJson = {"price": 104000}

        # default status code will be 200
        return json.dumps(priceJson)

    @mockWrapper
    def onMobileManufacturerRequest(self, **kwargs):
        """
        callback function for the route GET: /mobiles/manufacturers
        """

        return json.dumps(["samsung", "apple", "mi"]), 200

    @mockWrapper
    def onSearchRequest(self, **kwargs):
        """
        callback function for the route GET: /mobiles
        """

        # example of how to read url params /mobiles?search=samsung
        search = kwargs.get('request').args.get("q")
        models = []
        if search.lower() == "samsung":
            models = [{"model": "galaxy_a8", "price": 52000}, {"model": "galaxy_s9", "price": 54000}]
        elif search.lower() == "apple":
            models = [{"model": "xs", "price": 104000}, {"model": "xr", "price": 88000}]

        # default status code will be 200
        return json.dumps(models)

    @mockWrapper
    def onMobilesPost(self, **kwargs):
        """
        callback function for the route POST: /mobiles
        """

        code = 201
        return json.dumps({"message": "successfully created"}), code

    @mockWrapper
    def bad_request(self, **kwargs):
        """
        callback function for the route GET: /tablets
        """

        code = 400
        msg = {"message": "error message"}
        return json.dumps(msg), code

    def initialise(self):

        self.daemon = True
        self.start()

        # adding little sleep as start & shutdown mock server very often creates connection problems
        time.sleep(0.5)

        # putting this code inside run() doesn't work
        # requires callback function to prepare response which needs to be returned
        self.add_response_callback(url = "/mobiles/<manufacturer>/<model>", callback = self.onMobileModelInfo,
                                   methods = ["GET"])

        self.add_response_callback(url = "/mobiles/manufacturers", callback = self.onMobileManufacturerRequest,
                                   methods = ["GET"])

        self.add_response_callback(url = "/mobiles", callback = self.onSearchRequest, methods = ["GET"])

        self.add_response_callback(url = "/mobiles", callback = self.onMobilesPost, methods = ["post"])
        self.add_response_callback(url = "/tablets", callback = self.bad_request, methods = ["GET"])
