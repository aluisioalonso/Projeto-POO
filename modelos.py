class Pessoa:
    def __init__(self, name, cpf, password):
        self.__name = name
        self.__cpf = cpf
        self.__password = password

    @property
    def name(self):
        return self.__name

    @property
    def cpf(self):
        return self.__cpf

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, new_pw):
        self.__password = new_pw

    def role(self):
        return "Common User"


class User(Pessoa):
    pass


class Admin(Pessoa):
    def role(self):
        return "Administrator"


class Investor:
    def __init__(self, holdings):
        self.__holdings = holdings  # Lista de dicionários com stocks do usuário

    @property
    def holdings(self):
        return self.__holdings

    def _earn(self, rate):
        results = []
        if not self.__holdings:
            return results
        for h in self.__holdings:
            value = h["quantity"] * h["value"] * rate
            results.append((h["name"], value))
        return results

    def dividends(self):
        return self._earn(0.02)

    def jcp(self):
        return self._earn(0.015)


