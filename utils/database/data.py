import codecs
import json


class UserData:
    def __init__(self):
        with codecs.open("./data/user_data.json", "r", "utf-8") as f:
            self.data = json.loads(f.read())

        self.open_()

    def dict_(self, *parameters, chat_id: int | None = None):
        """
            Retrieve user data as a dictionary based on specified parameters.

            The function filters user data and returns a dictionary where the keys
            are user chat IDs and the values depend on the provided parameters:
            - If no parameters are provided, it returns the entire user data dictionary.
            - If one parameter is provided, it returns the value of that parameter for each user.
            - If multiple parameters are provided, it returns a dictionary containing only those parameters for each user.

            Optionally, the function can filter data for a specific chat ID.

            Args:
                *parameters: Arbitrary list of strings specifying which user data parameters to retrieve.
                chat_id (int, optional): Specific chat ID to filter the user data.

            Returns:
                dict: A dictionary with chat IDs as keys and user data as values.

        """
        self.open_()
        result = dict()
        match len(parameters):
            case 0:
                for user in self.data:
                    if chat_id is None:
                        result[user["chat_id"]] = user
                    else:
                        if user["chat_id"] == chat_id:
                            result[user["chat_id"]] = user
                            break
            case 1:
                for user in self.data:
                    if chat_id is None:
                        result[user["chat_id"]] = user[parameters[0]]
                    else:
                        if user["chat_id"] == chat_id:
                            result[user["chat_id"]] = user[parameters[0]]
            case _:
                for user in self.data:
                    if chat_id is None:
                        result[user["chat_id"]] = dict()
                        for parameter in parameters:
                            result[user["chat_id"]][parameter] = user[parameter]
                    else:
                        if user["chat_id"] == chat_id:
                            result[user["chat_id"]] = dict()
                            for parameter in parameters:
                                result[user["chat_id"]
                                       ][parameter] = user[parameter]
                            break

        self.log.write(
            f"UserData.dict with parameters {parameters} and chat_id {chat_id} generated the next result:\n\n")
        self.log.write("\n".join([" -- " + str(key) + "  =  " + str(value)
                       for key, value in result.items()]) + "\n\n")
        self.log.close()
        return result

    def add(self, chat_id: int, **kwargs) -> None:
        '''
        Adds a new user to the database with the given chat_id and keyword arguments.

        For example, if you want to add a user with a language of 'en' and a level of 'A', you would do:

        >>> user_data.add("12345678", languages=["en"], level=["A"])

        It will then be written to the user_data.json file.
        '''
        self.open_()
        if self.is_chat(chat_id):
            self.log.write(
                f"WARNING Using add() on existing chat_id, not adding new entry to database. To update data use update() instead. \n")
        else:
            self.data.append({"chat_id": chat_id, **kwargs})
            self._write()
        self.log.close()

    def update(self, chat_id: int, **kwargs) -> None:
        self.open_()
        self.log.write("Updating user data for chat_id " +
                       str(chat_id) + ". Args:\n" + str(kwargs) + "\n")
        if self.is_chat(chat_id):
            for user in self.data:
                if user["chat_id"] == chat_id:
                    for key, value in kwargs.items():
                        user[key] = value
        else:
            self.add(chat_id, **kwargs)
        self._write()

    def is_chat(self, chat_id: int) -> bool:
        '''
        Returns True if the given chat_id exists in the database, False otherwise.
        '''
        return chat_id in list(user["chat_id"] for user in self.data)

    def _write(self) -> None:
        '''
        Writes the current state of the user data to the user_data.json file.
        '''
        self.open_()
        with codecs.open("./data/user_data.json", "w", "utf-8") as f:
            self.log.write("Writing user data to user_data.json:\n\n")
            self.log.write("NEW -- " + json.dumps(self.data, indent=4) + "\n")
            self.log.write("OLD -- " + str(self.data) + "\n\n")
            f.write(json.dumps(self.data, indent=4))
        self.log.write("User data written to user_data.json\n\n")
        self.log.close()

    def open_(self) -> None:
        self.log = codecs.open("./data/log.txt", "a", "utf-8")
