"""
Log Climbs
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from pathlib import Path
import sqlite3
import asyncio



lightGreen = "#8CEFB6"
darkGreen = "#6DBCB9"
lightBlue = "#4888B7"
darkBlue = "#474476"
purple = "#372134"

buttonStyle = Pack(background_color = darkGreen)
dataEntryStyle = Pack(background_color = "white")



class Entry():
    def __init__(self, ID, date, type, grade, attempts, notes):
        self.__ID = ID
        self.__date = date
        self.__type = type
        self.__grade = grade
        self.__attempts = attempts
        self.__notes = notes

    def getID(self):
        return self.__ID
    
    def getFormattedDate(self):
        return f"{self.__date[8:]}/{self.__date[5:7]}/{self.__date[0:4]}"
    
    def getSortDate(self):
        return int(self.__date.replace("-", ""))
    
    def getDate(self):
        return self.__date
    
    def getType(self):
        return self.__type
    
    def getGrade(self):
        return self.__grade
    
    def getSortGrade(self):
        leadGrades = ["a", "a+", "b", "b+", "c", "c+"]
        if self.__grade[0] == "V":
            return int(self.__grade[1:])
        else:
            return int(f"{self.__grade[0]}{leadGrades.index(self.__grade[1:])}")
        
    
    def getAttempts(self):
        return self.__attempts
    
    def getNotes(self):
        return self.__notes

    def getDetails(self):
        return f"{self.__type}: {self.__grade}, {self.__notes}"



class Chalked(toga.App):
    def startup(self):


        #Checking for/creating database
        self.path = self.paths.data / "entriesDatabase.db"
        try:
            database = open(self.path, "x")
            self.connectToDB()
            self.cur.execute("CREATE TABLE 'Entries' ('ID' INTEGER, 'Date' TEXT, 'Type' TEXT, 'Grade' TEXT, 'Attempts' TEXT, 'Notes' TEXT);")
        except:
            self.connectToDB()


        #Defining navbar
        self.navBox = toga.Box(direction = ROW, background_color = darkBlue)
        self.homeButton = toga.Button("Home", on_press = self.switchScreenMain, background_color = darkGreen, flex = 1)
        self.addButton = toga.Button("Add Entry", on_press = self.switchScreenAdd, background_color = darkGreen, flex = 1)
        self.navBox.add(toga.Box(flex = 1), self.homeButton,toga.Box(flex = 1), self.addButton, toga.Box(flex = 1))


        #Initalising mainBox + main_window, and defining inital content
        self.mainBox = toga.Box(direction = COLUMN, flex = 1)
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.switchScreenMain(None)
        self.main_window.show()


    #Sets up DB connection
    def connectToDB(self):
        self.con = sqlite3.connect(self.path)
        self.cur = self.con.cursor()
    
    #Returns DB cursor object
    def getCursor(self):
        return self.cur

    #Switches mainBox content and updates main_window
    def switchScreen(self, newScreen):
        self.activeScreen = newScreen
        self.mainBox.clear()
        self.mainBox.add(self.activeScreen.getContent(), self.navBox)
        self.main_window.content = self.mainBox

    #Handler for home button
    def switchScreenMain(self, widget):
        self.switchScreen(MainScreen(self))

    #Handler for add button
    def switchScreenAdd(self, widget):
        self.switchScreen(AddScreen(self))



class MainScreen():
    def __init__(self, app):
        self.app = app
        self.cur = app.getCursor()
        self.entries = []

        self.sortDirection = "Desc"
        self.currentSort = "Date"

        #Defining Layout Boxes
        self.contentBox = toga.Box(direction = COLUMN, flex = 1)
        self.filterBox = toga.Box(direction = ROW, background_color = darkBlue)
        self.sortBox = toga.Box(direction = ROW, alignment = CENTER, background_color = lightBlue)
        self.listBox = toga.Box(direction = COLUMN, flex = 1)

        #Defining Widgets
        self.filter1 = toga.Button("Lead Climbs", on_press = self.filterLead, flex = 1, style = buttonStyle)
        self.filter2 = toga.Button("Boulders", on_press = self.filterBoulder, flex = 1, style = buttonStyle)
        self.reset = toga.Button("Reset", on_press = self.resetFilter, style = buttonStyle)

        self.sortLabel = toga.Label(text = "Sort By:")
        self.sortDate = toga.Button(text = "Date", style = buttonStyle, on_press = self.sortByDate, flex = 1)
        self.sortGrade = toga.Button(text = "Grade", style = buttonStyle, on_press = self.sortByGrade, flex = 1)
        self.sortArrow = toga.Button(icon = "resources/arrow-down.png", style = buttonStyle, on_press = self.changeSortDirection)

        self.table = toga.DetailedList(primary_action = "View/Edit", on_primary_action = self.viewItem, secondary_action = "Delete", on_secondary_action = self.deleteItem, flex = 1, background_color = "#8CEFB6")

        #Adding Widgets to Boxes
        self.contentBox.add(self.filterBox, self.sortBox, self.listBox)
        self.filterBox.add(self.filter1, self.filter2, self.reset)
        self.sortBox.add(self.sortLabel, self.sortDate, self.sortGrade, self.sortArrow)
        self.listBox.add(self.table)

        self.resetFilter(None)
        self.sortByDate(None)

    def insertionSort(self, getData):
        n = len(self.entries)
        for i in range(1,n):
            insert_index = i
            current_value = self.entries.pop(i)
            for j in range(i-1, -1, -1):
                if (getData(self.entries[j]) < getData(current_value) and self.sortDirection == "Desc") or (getData(self.entries[j]) > getData(current_value) and self.sortDirection == "Asc"):
                    insert_index = j
                else:
                    break
            self.entries.insert(insert_index, current_value)
        self.updateTable()
    
    def sortByDate(self, widget):
        self.insertionSort(lambda entry: entry.getSortDate())
        self.currentSort = "Date"
        self.sortDate.background_color = lightGreen
        self.sortGrade.background_color = darkGreen

    def sortByGrade(self, widget):
        self.insertionSort(lambda entry: entry.getSortGrade())
        self.currentSort = "Grade"
        self.sortGrade.background_color = lightGreen
        self.sortDate.background_color = darkGreen

    def changeSortDirection(self, widget):
        if self.sortDirection == "Desc":
            self.sortDirection = "Asc"
            self.sortArrow.icon = "resources/arrow-up"
        elif self.sortDirection == "Asc":
            self.sortDirection = "Desc"
            self.sortArrow.icon = "resources/arrow-down"
        self.updateSort()
        
    def updateSort(self):
        if self.currentSort == "Date":
            self.sortByDate(None)
        elif self.currentSort == "Grade":
            self.sortByGrade(None)


    def filterList(self, type):
        newList = []
        for row in self.cur.execute(f"SELECT * FROM Entries WHERE Type LIKE '{type}%';"):
            newList.append(Entry(row[0], row[1], row[2], row[3], row[4], row[5]))
        self.entries = newList
        self.updateSort()
        self.updateTable()

        self.reset.enabled = True
        
    def filterLead(self, widget):
        self.filterList("Lead")
        self.filter1.background_color = lightGreen
        self.filter2.background_color = darkGreen

    def filterBoulder(self, widget):
        self.filterList("Boulder")
        self.filter2.background_color = lightGreen
        self.filter1.background_color = darkGreen

    def resetFilter(self, widget):
        self.filterList("%")
        self.reset.enabled = False
        self.filter2.background_color = darkGreen
        self.filter1.background_color = darkGreen


    def updateTable(self):
        self.table.data.clear()

        for i in self.entries:
            self.table.data.append({
                "icon": None,
                "title": i.getFormattedDate(),
                "subtitle": i.getDetails(),
                "data": i.getID()
            })


    def deleteItem(self, widget, row):
        self.cur.execute(f"DELETE FROM Entries WHERE ID = '{row.data}';")
        self.entries.pop(row.data)
        self.app.con.commit()
        self.updateTable()

    def viewItem(self, widget, row):
        self.app.switchScreen(AddScreen(self.app, row.data))


    def getContent(self):
        return self.contentBox



class AddScreen():
    def __init__(self, app, rowID = None):
        self.app = app
        self.cur = app.getCursor()
        self.rowID = rowID

        self.gradeIndex = 0
        self.attemptsIndex = 0

        #Defining Layout Boxes
        self.contentBox = toga.Box(direction = COLUMN, flex = 1, gap = 1, background_color = purple)

        self.typeBox = toga.Box(direction = ROW, flex = 1, align_items = CENTER, background_color = lightBlue, gap = 50)
        self.dateBox = toga.Box(direction = ROW, flex = 2, align_items = CENTER, background_color = lightGreen)
        self.gradeBox = toga.Box(direction = ROW, flex = 2, align_items = CENTER, background_color = lightGreen)
        self.gradeEntryBox = toga.Box(direction = ROW, flex = 3, align_items = CENTER)
        self.attemptsBox = toga.Box(direction = ROW, flex = 2, align_items = CENTER, background_color = lightGreen)
        self.attemptsEntryBox = toga.Box(direction = ROW, flex = 3, align_items = CENTER)
        self.notesBox = toga.Box(direction = ROW, flex = 2, align_items = CENTER, background_color = lightGreen)
        self.buttonBox = toga.Box(direction = ROW, flex = 1, align_items = CENTER, background_color = lightBlue)

        #Defining Widgets
        self.leadButton = toga.Button(text = "Lead", style = buttonStyle, on_press = self.leadType, flex = 1)
        self.boulderButton = toga.Button(text = "Boulder", style = buttonStyle, on_press = self.boulderType, flex = 1)

        self.dateLabel = toga.Label(text = "Date:", flex = 1)
        self.dateInput = toga.DateInput(flex = 3, style = dataEntryStyle)

        self.gradeLabel = toga.Label(text = "Grade:", flex = 1)
        self.numberSelection = toga.Selection(items = ["4", "5", "6", "7", "8", "9"], flex = 1, style = dataEntryStyle)
        self.gradeDecrease = toga.Button(text = "-", style = buttonStyle, on_press = self.decreaseGrade, flex = 1)
        self.gradeInput = toga.Label(text = None, style = dataEntryStyle, flex = 1)
        self.gradeIncrease = toga.Button(text = "+", style = buttonStyle, on_press = self.increaseGrade, flex = 1)
        self.gradeEntryBox.add(self.gradeDecrease, self.gradeInput, self.gradeIncrease)

        self.attemptsValues = ["FLASH", "2", "3", "4", "5+", "PROJ"]
        self.attemptsLabel = toga.Label(text = "Attempts:", flex = 1)
        self.attemptsDecrease = toga.Button(text = "-", style = buttonStyle, on_press = self.decreaseAttempts, flex = 1)
        self.attemtpsInput = toga.Label(text = self.attemptsValues[0], flex = 1, style = dataEntryStyle)
        self.attemptsIncrease = toga.Button(text = "+", style = buttonStyle, on_press = self.increaseAttempts, flex = 1)
        self.attemptsEntryBox.add(self.attemptsDecrease, self.attemtpsInput, self.attemptsIncrease)

        self.notesLabel = toga.Label(text = "Notes:", flex = 1)
        self.notesInput = toga.MultilineTextInput(flex = 3, style = dataEntryStyle)

        #Check if editing or making new entry
        if rowID == None:
            self.Button = toga.Button(direction = ROW, text = "Add", flex = 1, on_press = self.addEntry, style = buttonStyle)
            self.leadType(None)
        else:
            self.Button = toga.Button(direction = ROW, text = "Update", flex = 1, on_press = self.updateEntry, style = buttonStyle)
            self.selectedRow = Entry(*next(self.app.cur.execute(f"SELECT * FROM Entries WHERE ID = {self.rowID}")))

            if self.selectedRow.getType() == "Boulder":
                self.boulderType(None)
                self.gradeInput.text = self.selectedRow.getGrade()
                self.gradeIndex = self.gradeValues.index(self.gradeInput.text)
            if self.selectedRow.getType() == "Lead":
                self.leadType(None)
                self.numberSelection.value = self.selectedRow.getGrade()[0:1]
                self.gradeInput.text = self.selectedRow.getGrade()[1:]
                self.gradeIndex = self.gradeValues.index(self.gradeIndex.text)

            self.dateInput.value = self.selectedRow.getDate()
            self.attemtpsInput.text = self.selectedRow.getAttempts()
            self.attemptsIndex = self.attemptsValues.index(self.attemtpsInput.text)
            self.notesInput.value = self.selectedRow.getNotes()

        #Adding Widgets to Boxes
        self.typeBox.add(self.leadButton, self.boulderButton)
        self.dateBox.add(self.dateLabel, self.dateInput)
        self.gradeBox.add(self.gradeLabel, self.gradeEntryBox)
        self.attemptsBox.add(self.attemptsLabel, self.attemptsEntryBox)
        self.notesBox.add(self.notesLabel, self.notesInput)
        self.buttonBox.add(self.Button)

        self.contentBox.add(self.typeBox, self.dateBox, self.gradeBox, self.attemptsBox, self.notesBox, self.buttonBox)


    def leadType(self, widget):
        self.type = "Lead"
        self.leadButton.background_color = lightGreen
        self.boulderButton.background_color = darkGreen

        if self.numberSelection not in self.gradeEntryBox.children:
            self.gradeEntryBox.insert(0, self.numberSelection)

        self.gradeValues = ["a", "a+", "b", "b+", "c", "c+"]
        self.gradeInput.text = self.gradeValues[0]
        self.gradeIndex = 0

    def boulderType(self, widget):
        self.type = "Boulder"
        self.leadButton.background_color = darkGreen
        self.boulderButton.background_color = lightGreen

        self.gradeEntryBox.remove(self.numberSelection)

        self.gradeValues = [f"V{i}" for i in range(0,18)]
        self.gradeInput.text = self.gradeValues[0]
        self.gradeIndex = 0


    def decreaseGrade(self, widget):
        self.gradeIndex = self.changeValue(self.gradeIndex, self.gradeValues, "-", self.gradeInput)

    def increaseGrade(self, widget):
        self.gradeIndex = self.changeValue(self.gradeIndex, self.gradeValues, "+", self.gradeInput)

    def decreaseAttempts(self, widget):
        self.attemptsIndex = self.changeValue(self.attemptsIndex, self.attemptsValues, "-", self.attemtpsInput)

    def increaseAttempts(self, widget):
        self.attemptsIndex = self.changeValue(self.attemptsIndex, self.attemptsValues, "+", self.attemtpsInput)

    def changeValue(self, index, valueList, direction, targetWidget):
        if direction == "+":
            index += 1
        elif direction == "-":
            index -= 1

        index = max(0, min(index, len(valueList)-1))
        targetWidget.text = valueList[index]
        return index


    async def addEntry(self, widget):
        grade = self.getGradeValue()
        try:
            previousID = next(self.cur.execute("SELECT MAX(ID) FROM Entries;"))[0]
            nextID = previousID + 1
        except:
            nextID = 0

        self.cur.execute(f"INSERT INTO Entries VALUES ('{nextID}', '{self.dateInput.value}', '{self.type}', '{grade}', '{self.attemtpsInput.text}', '{self.notesInput.value}');")
        self.app.con.commit()
        self.gradeInput.value = None
        self.attemtpsInput.value = None
        self.notesInput.value = None
        addedEntryDialog = toga.InfoDialog("Entry Added", "Entry Added to Database")
        await self.app.main_window.dialog(addedEntryDialog)

    async def updateEntry(self, widget):
        grade = self.getGradeValue()
        self.cur.execute(f"UPDATE Entries SET date = '{self.dateInput.value}', type = '{self.type}', grade = '{grade}', attempts = '{self.attemtpsInput.text}', notes = '{self.notesInput.value}' WHERE ID = {self.rowID}")
        self.app.con.commit()
        updatedEntryDialog = toga.InfoDialog("Entry Updated", f"Entry Updated in Database")
        await self.app.main_window.dialog(updatedEntryDialog)

    def getGradeValue(self):
        if self.type == "Lead":
            grade = f"{self.numberSelection.value}{self.gradeInput.text}"
        elif self.type == "Boulder":
            grade = f"{self.gradeInput.text}"
        return grade


    def getContent(self):
        return self.contentBox



def main():
    return Chalked()