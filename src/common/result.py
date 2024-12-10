from flask import Response, jsonify
class Result:
    """ 结果类 """
    def __init__(self, code: int, message: str=None, data: any=None):
        self._code: int = code
        self._message: str = message
        self._data = data

    @property
    def code(self) -> int:
        return self._code

    @property
    def message(self) -> str:
        return self._message

    @property
    def data(self) -> any:
        return self._data

    # 将result直接作为flask响应
    def as_response(self) -> Response:
        response = jsonify({'message': self.message, 'data': self.data})
        response.status_code = self._code
        return response

    # 将result作为字典
    def as_dict(self) -> dict:
        return {
            'code': self._code,
            'message': self._message,
            'data': self._data
        }

    def __str__(self):
        return ('{code: %(code)s, message: %(message)s, data: %(data)s}' %
                   {'code': self.code, 'message': self.message, 'data': self.data})