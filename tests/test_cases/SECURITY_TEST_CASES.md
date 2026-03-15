# Dokumentacja Przypadków Testowych

Ten dokument zawiera opisy testów jednostkowych dla modułu bezpieczeństwa (`app.core.security`).

## Testy Security & JWT

| ID | Tytuł | Dane wejściowe | Kroki testowe | Oczekiwany rezultat |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | **Haszowanie: Maskowanie hasła** | `password123` | 1. Przekaż jawne hasło do funkcji `hash_password`. <br> 2. Sprawdź typ danych wyjściowych. <br> 3. Porównaj wynik z hasłem jawnym. | 1. Wynik jest ciągiem znaków (string). <br> 2. Hasło w bazie nie jest czytelne (zostało zahaszowane). |
| **TC-02** | **Haszowanie: Unikalność soli (Salt)** | `password123` | 1. Wykonaj haszowanie tego samego hasła dwukrotnie. <br> 2. Porównaj oba wyniki (hasze) ze sobą. | Wyniki różnią się od siebie mimo identycznego wejścia (zabezpieczenie przed atakami słownikowymi). |
| **TC-03** | **Weryfikacja: Poprawne dane** | `bezpieczne_haslo123` | 1. Wygeneruj hasz dla podanego hasła. <br> 2. Przekaż to samo hasło oraz ten hasz do funkcji `verify_password`. | System zwraca wartość `True`. |
| **TC-04** | **Weryfikacja: Znaki specjalne i UTF-8** | `zażółć gęślą jaźń!@#` | 1. Wprowadź hasło zawierające polskie znaki, spacje i symbole. <br> 2. Zahaszuj i spróbuj zweryfikować. | System poprawnie obsługuje kodowanie znaków; wynik weryfikacji to `True`. |
| **TC-05** | **Weryfikacja: Błędne hasło** | `user_pass`, `wrong_pass` | 1. Zahaszuj ciąg `user_pass`. <br> 2. Spróbuj zweryfikować go, podając jako hasło jawne `wrong_pass`. | System zwraca `False` (odmowa dostępu). |
| **TC-06** | **JWT: Generowanie tokenu** | `user_id: "789"` | 1. Wywołaj funkcję `create_access_token` dla ID użytkownika. <br> 2. Sprawdź, czy zwrócono niepusty ciąg znaków. | Otrzymano poprawnie sformatowany, zakodowany token JWT. |
| **TC-07** | **JWT: Zawartość Payload (Subject)** | `sub: "test_user"` | 1. Wygeneruj token JWT. <br> 2. Zdekoduj token przy użyciu klucza tajnego i algorytmu. <br> 3. Odczytaj wartość pola `sub`. | Pole `sub` zawiera dokładnie wartość `"test_user"`. |
| **TC-08** | **JWT: Dekodowanie sprawnego tokenu** | Aktywny token JWT | 1. Przekaż poprawny, ważny czasowo token do `decode_access_token`. | Funkcja zwraca identyfikator użytkownika (String). |
| **TC-09** | **JWT: Obsługa wygasłego tokenu** | Token z `exp < now` | 1. Stwórz token, którego czas ważności (timedelta) jest ujemny. <br> 2. Spróbuj go zdekodować funkcją systemową. | System rozpoznaje wygaśnięcie i zwraca `None`. |
| **TC-10** | **JWT: Odporność na błędne dane** | `None`, `""`, `malformed.jwt` | 1. Przekaż do funkcji dekodującej dane uszkodzone lub puste. <br> 2. Sprawdź stabilność aplikacji. | System nie rzuca nieobsłużonym błędem; funkcja bezpiecznie zwraca `None`. |