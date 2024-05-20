from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
import pandas as pd
from urllib.parse import unquote
import sqlite3

app = FastAPI()
conn = sqlite3.connect('phone.db')
curs = conn.cursor()

curs.execute("CREATE TABLE IF NOT EXISTS phoneTable ("
             "id INTEGER PRIMARY KEY,"
             "FIO TEXT NOT NULL,"
             "phoneNumber TEXT NOT NULL,"
             "CABINET TEXT NULL)")
conn.commit()
conn.close()

search_page = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Телефонная база</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
      background-color: #f4f4f4;
    }

    #header {
      background-color: #333;
      color: #fff;
      padding: 15px;
      text-align: center;
    }

    #searchContainer {
      text-align: center;
      margin: 50px auto;
    }

    #search_text {
      padding: 10px;
      font-size: 16px;
      width: 80%;
      max-width: 400px;
    }
    
    #searchResults {
  margin: 50px auto;
  margin-top: 20px;
  padding: 20px;
  background-color: #ecf0f1;
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: opacity 0.5s ease-in-out;
  text-align: center;
  opacity: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}
  </style>
</head>
<body>

<div id="header">
  <h1>Телефонная база</h1>
</div>

<div id="searchContainer">
  <input type="text" id="search_text" placeholder="Введите ФИО, номер или кабинет" oninput="searchData()">
  <div id="searchResults"></div>
</div>
    <script>
        async function searchData() {
            const search_text = document.getElementById("search_text").value;
            const resultsContainer = document.getElementById("searchResults");

            if (search_text.length === 0) {
                resultsContainer.innerHTML = "";
                resultsContainer.style.opacity = 0;
                return;
            }

            const response = await fetch("/search/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: `search_text=${search_text}`,
            });

            const resultHtml = await response.text();
            resultsContainer.innerHTML = resultHtml;
            resultsContainer.style.opacity = 1;
        }
    </script>
</body>
</html>
"""

excel_file_path = "123.xlsx"

excel_data = pd.read_excel(excel_file_path)

excel_data["Номер"] = excel_data["Номер"].astype('Int64').astype(str)


@app.get("/")
async def main():
    return HTMLResponse(content=search_page, status_code=200)


@app.post("/search/")
async def search_data(search_text: str = Form(...)):
    global excel_data
    if excel_data is None:
        raise HTTPException(status_code=400, detail="Укажите файл -excel_file_path- тут")

    search_text = unquote(search_text).encode('latin-1').decode('utf-8')
    search_text = search_text.lower()
    if search_text.isdigit():
        filtered_data = excel_data[excel_data["Номер"].str.contains(search_text, na=False)]
    elif search_text[:-1].isdigit():
        print(search_text)
        filtered_data = excel_data[excel_data["Кабинет"].str.lower().str.contains(search_text, na=False)]
    else:
        filtered_data = excel_data[excel_data["ФИО"].str.lower().str.contains(search_text, na=False)]

    if filtered_data.empty:
        return HTMLResponse(content="Ничего не найдено", status_code=200)

    results_html = filtered_data.to_html(index=False)
    return HTMLResponse(content=results_html, status_code=200)


if __name__ == '__main__':
    from os import system

    system('uvicorn stik5:app --reload')
