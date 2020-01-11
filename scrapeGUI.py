import os
import os.path
import tkinter
from datetime import date
from tkinter import Tk, Listbox, END
from tkinter import ttk

import requests
from bs4 import BeautifulSoup

today = date.today()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0"}


class DeckMGT(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.generateIntroGUI()

    def generateIntroGUI(self):
        for widget in self.parent.winfo_children():  # clear frame on load
            widget.destroy()
        self.parent.geometry("450x300")
        self.parent.title("Price Checker | Main Menu")

        self.labelTop = ttk.Label(self.parent, text="View Card History")
        self.labelTop.pack()

        cardNames = []  # populate a list of decklists
        if not os.listdir("Cards/"):
            cardNames.append("No cards in system")
        else:
            for each in os.listdir("Cards"):
                cardNames.append(each.replace(".txt", ""))
        self.cardNameComboBox = ttk.Combobox(self.parent, state="readonly", values=list(set(cardNames)),
                                             postcommand=self.updateList, width=25)
        self.cardNameComboBox.pack()
        self.cardNameComboBox.current(0)

        self.cardHistoryBtn = ttk.Button(self.parent, text="View", command=self.generateCardHistoryGUI)
        self.cardHistoryBtn.pack()

        self.cardHistoryBtn = ttk.Button(self.parent, text="Generate Price Report", command=self.generatePriceReport)
        self.cardHistoryBtn.pack()

        self.newURLEntry = ttk.Entry(self.parent)
        self.newURLEntry.pack()

        self.newCardBtn = ttk.Button(self.parent, text="Add New Card", command=self.generateNewCard)
        self.newCardBtn.pack()

        self.exitButton = ttk.Button(self.parent, text="Exit Application", command=self.exitApplication)
        self.exitButton.pack()

    def generateCardHistoryGUI(self):
        listbox = Listbox(Tk())
        listbox.configure(width=60, height=20)
        listbox.winfo_toplevel().title("Results for " + self.cardNameComboBox.get())
        listbox.configure()
        listbox.pack()

        for eachLine in open("Cards/" + self.cardNameComboBox.get() + ".txt", "r+", encoding="utf-8").readlines():
            listbox.insert(END, eachLine)

    def generatePriceReport(self):
        storedReports = []
        listbox = Listbox(Tk())
        listbox.configure(width=60, height=20)
        listbox.winfo_toplevel().title("Price Report")
        listbox.configure()
        listbox.pack()

        for each in open("URLs.txt"):
            soup = BeautifulSoup(requests.get(url=each, headers=headers).content, "html.parser")
            cardName = soup.find('h1', attrs={"class": "title"}).get_text().replace('/', '')
            if (soup.find('span', attrs={"class": "variant-short-info"}).get_text() == "Out of stock."):
                price = soup.find('span', attrs={"class": "price no-stock"}).get_text()[5:]
            else:
                price = soup.find('span', attrs={"class": "regular price"}).get_text()[5:]

            if (os.path.exists("Cards/" + cardName + ".txt")):
                eachLastLine = open("Cards/" + cardName + ".txt", "r+", encoding="utf-8").readlines()[-1].split("|", 1)[
                    0].strip()
            if (eachLastLine != price):
                storedReports.append(cardName + " changed price from " + str(eachLastLine) + " to " + price)
                open("Cards/" + cardName + ".txt", "a", encoding="utf-8").write(
                    price + " | " + str(date.today()) + "\n")
            else:
                eachLastLine = open("Cards/" + cardName + ".txt", "w", encoding="utf-8").write(
                    price + " | " + str(date.today()) + "\n")

        if (len(storedReports) == 0):
            listbox.insert(END, "NO CHANGES!")
        else:
            for eachLine in storedReports:
                listbox.insert(END, eachLine)

    def generateNewCard(self):
        soup = BeautifulSoup(requests.get(url=self.newURLEntry.get(), headers=headers).content, "html.parser")
        newCard = open("Cards/" + soup.find('h1', attrs={"class": "title"}).get_text().replace('/', '') + ".txt", "w")
        if (soup.find('span', attrs={"class": "variant-short-info"}).get_text() == "Out of stock."):
            newCard.write(
                soup.find('span', attrs={"class": "price no-stock"}).get_text()[5:] + " | " + str(date.today()) + "\n")
        else:
            newCard.write(
                soup.find('span', attrs={"class": "regular price"}).get_text()[5:] + " | " + str(date.today()) + "\n")
        newCard = open("URLs.txt", "a")
        newCard.write(self.newURLEntry.get() + "\n")
        newCard.close()
        self.newURLEntry.delete(0, END)

    def updateList(self):
        cardNames = []  # populate a list of decklists
        for each in os.listdir("Cards"):
            cardNames.append(each.replace(".txt", ""))

        self.cardNameComboBox.configure(values=list(set(cardNames)))  # updates decklist combobox on action

    def exitApplication(self):
        root.destroy()


if __name__ == '__main__':
    root = tkinter.Tk()
    ttk.Style().configure("TButton", padding=6, relief="flat", background="#666666")
    run = DeckMGT(root)
    root.mainloop()
