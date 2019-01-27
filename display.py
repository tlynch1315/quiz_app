import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5 import QtCore, QtGui
from quizui import Ui_Form
import requests
import json
import random
import time
import html.parser as HTMLParser


# thread for scoring
# I think that this is the way to go where there is a thread to do the scoring
# then send signal from score thread to main thread to update UI
# but I could be totally wrong
class scoreThread(QtCore.QThread):
    signal = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QtCore.QThread.__init__(self)


    def run(self):

        # I think you need to send a signal to the main thread to update the questions and answers
        if self.ans == self.correct:
            self.signal.emit('Correct')
        else:
            self.signal.emit('Incorrect')


class mainWindow(QMainWindow, Ui_Form):
    def __init__(self):

        # NEED TO KEEP
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # max value of 10 for progress bar, current is 0
        self.progressBar.setMaximum(10)
        self.progressBar.setValue(0)

        # get questions
        self.questions = self.getQuestions()

        # here is where I'm getting confused
        # We need to set it up so that any time a pushButton is clicked it scores the question and updates
        # to display the new question and answers
        self.scoreThread = scoreThread()
        self.scoreThread.signal.connect()
        self.pushButton.clicked.connect(self.scoreQuestions)

    # get questions from open Trivia API
    def getQuestions(self):
        re = requests.get("https://opentdb.com/api.php?amount=10&type=multiple")
        data = json.loads(re.text)
        return data['results']

    # this updates the questions and answers
    def nextQuestion(self):
        curr = self.questions.pop()
        answers = [curr['correct_answer']]
        answers.extend(curr['incorrect_answers'])
        random.shuffle(answers)
        if len(self.questions) == 0:
            return

        # display question
        self.textBrowser.setText(HTMLParser.HTMLParser().unescape(curr['question']))

        # display answers
        self.pushButton.setText(HTMLParser.HTMLParser().unescape(answers[0]))
        self.pushButton_2.setText(HTMLParser.HTMLParser().unescape(answers[1]))
        self.pushButton_3.setText(HTMLParser.HTMLParser().unescape(answers[2]))
        self.pushButton_4.setText(HTMLParser.HTMLParser().unescape(answers[3]))

        self.pushButton.setDisabled(False)

        # this was put in before bc I thought you might have to disconnect buttons when you update their values
        self.pushButton.disconnect()
        self.pushButton_2.disconnect()
        self.pushButton_3.disconnect()
        self.pushButton_4.disconnect()

        # do not think that this is correct
        self.pushButton.clicked.connect(lambda: self.scoreQuestion(self.pushButton.text(), curr['correct_answer']))
        self.pushButton_2.clicked.connect(lambda: self.scoreQuestion(self.pushButton_2.text(), curr['correct_answer']))
        self.pushButton_3.clicked.connect(lambda: self.scoreQuestion(self.pushButton_3.text(), curr['correct_answer']))
        self.pushButton_4.clicked.connect(lambda: self.scoreQuestion(self.pushButton_4.text(), curr['correct_answer']))


    def scoreQuestion(self, ans, correct):
        if ans == correct:
            self.textBrowser.setText("CORRECT")
        else:
            self.textBrowser.setText("INCORRECT")
        time.sleep(1)
        self.nextQuestion()




if __name__ == "__main__":
    random.seed()
    app = QApplication(sys.argv)
    form = mainWindow()
    form.show()
    sys.exit(app.exec_())
