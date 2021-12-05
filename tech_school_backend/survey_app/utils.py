import random, string


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
        """
        Функция для генерации рандомной строки.
        Используется для создания индивидуальной ссылки в models.
        """
        return ''.join(random.choice(chars) for _ in range(size))