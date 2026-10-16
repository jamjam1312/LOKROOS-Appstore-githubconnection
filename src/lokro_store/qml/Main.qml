pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    width: 1180
    height: 760
    minimumWidth: 900
    minimumHeight: 600
    visible: true
    title: "LOKRO Store — Alpha"
    color: "#090b0f"

    property color ink: "#f5f7fb"
    property color muted: "#98a2b3"
    property color panel: "#11151c"
    property color raised: "#181e27"
    property color line: "#29313d"
    property color accent: "#ffffff"
    property var selectedItem: null
    property QtObject storeBackend: null

    header: ToolBar {
        height: 76
        background: Rectangle { color: "#0c0f14"; border.color: window.line }
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 26
            anchors.rightMargin: 26
            spacing: 18
            Label {
                text: "// LOKRO STORE"
                color: window.ink
                font.pixelSize: 22
                font.bold: true
                Layout.preferredWidth: 220
            }
            TextField {
                id: search
                Layout.fillWidth: true
                Layout.maximumWidth: 560
                placeholderText: "Apps, Aufgaben oder Kategorien suchen …"
                color: window.ink
                placeholderTextColor: "#667085"
                background: Rectangle { radius: 12; color: window.raised; border.color: search.activeFocus ? "#ffffff" : window.line }
                onTextChanged: window.storeBackend.setSearch(text)
            }
            Item { Layout.fillWidth: true }
            Button {
                text: window.storeBackend.busy ? "Bitte warten …" : "Katalog aktualisieren"
                enabled: !window.storeBackend.busy
                onClicked: window.storeBackend.refreshCatalog()
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.preferredWidth: 230
            Layout.fillHeight: true
            color: "#0c0f14"
            border.color: window.line

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 10
                Label { text: "BEREICHE"; color: window.muted; font.pixelSize: 11; font.bold: true }
                ListView {
                    id: categories
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    model: window.storeBackend.categories
                    currentIndex: 0
                    spacing: 4
                    delegate: ItemDelegate {
                        required property int index
                        required property string modelData
                        width: categories.width
                        height: 42
                        text: modelData
                        highlighted: ListView.isCurrentItem
                        onClicked: { categories.currentIndex = index; window.storeBackend.setCategory(modelData) }
                    }
                }
                Rectangle { Layout.fillWidth: true; height: 1; color: window.line }
                Label { text: "ALPHA 4"; color: window.muted; font.pixelSize: 11 }
                Label {
                    Layout.fillWidth: true
                    text: "Flathub-Apps und geprüfte Projektvorschauen. Designs folgen nach Prüfung."
                    color: window.muted
                    wrapMode: Text.WordWrap
                    font.pixelSize: 12
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 72
                color: window.panel
                border.color: window.line
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    Label {
                        text: search.text ? "Suchergebnisse" : "Entdecken"
                        color: window.ink
                        font.pixelSize: 26
                        font.bold: true
                    }
                    Item { Layout.fillWidth: true }
                    Label { text: window.storeBackend.items.length + " Einträge"; color: window.muted }
                }
            }

            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                background: Rectangle { color: window.color }

                GridView {
                    id: grid
                    anchors.fill: parent
                    anchors.margins: 22
                    cellWidth: 292
                    cellHeight: 220
                    model: window.storeBackend.items
                    boundsBehavior: Flickable.StopAtBounds
                    delegate: Rectangle {
                        required property var modelData
                        width: 272
                        height: 200
                        radius: 16
                        color: cardMouse.containsMouse ? "#202733" : window.panel
                        border.color: cardMouse.containsMouse ? "#4b5565" : window.line

                        MouseArea {
                            id: cardMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: window.selectedItem = modelData
                        }
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 18
                            spacing: 9
                            RowLayout {
                                Layout.fillWidth: true
                                Image {
                                    source: modelData.iconUrl
                                    sourceSize.width: 54
                                    sourceSize.height: 54
                                    Layout.preferredWidth: 54
                                    Layout.preferredHeight: 54
                                    fillMode: Image.PreserveAspectFit
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    Label { text: modelData.name; color: window.ink; font.pixelSize: 18; font.bold: true; elide: Text.ElideRight; Layout.fillWidth: true }
                                    Label { text: modelData.categoriesText; color: window.muted; font.pixelSize: 11; elide: Text.ElideRight; Layout.fillWidth: true }
                                }
                                Label { visible: modelData.featured; text: "TOP"; color: "#0b0d10"; font.bold: true; padding: 6; background: Rectangle { radius: 6; color: "#f8fafc" } }
                            }
                            Label { text: modelData.summary; color: window.ink; font.pixelSize: 14; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                            Label { text: modelData.description; color: window.muted; font.pixelSize: 12; Layout.fillWidth: true; Layout.fillHeight: true; wrapMode: Text.WordWrap; elide: Text.ElideRight; maximumLineCount: 2 }
                            RowLayout {
                                Layout.fillWidth: true
                                Label { text: modelData.license; color: "#667085"; font.pixelSize: 10; Layout.fillWidth: true; elide: Text.ElideRight }
                                Button {
                                    text: modelData.actionText
                                    enabled: modelData.actionEnabled && !window.storeBackend.busy
                                    onClicked: window.storeBackend.installOrUpdate(modelData.id)
                                }
                            }
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 42
                color: "#0c0f14"
                border.color: window.line
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 18
                    anchors.rightMargin: 18
                    BusyIndicator { running: window.storeBackend.busy; visible: running; Layout.preferredWidth: 22; Layout.preferredHeight: 22 }
                    Label { text: window.storeBackend.message; color: window.muted; Layout.fillWidth: true; elide: Text.ElideRight }
                    Label { text: "Keine beliebigen Download-Skripte"; color: "#667085"; font.pixelSize: 11 }
                }
            }
        }
    }

    Drawer {
        id: details
        edge: Qt.RightEdge
        width: Math.min(window.width * 0.42, 480)
        height: window.height
        modal: true
        interactive: true
        onClosed: window.selectedItem = null
        Connections {
            target: window
            function onSelectedItemChanged() { if (window.selectedItem) details.open() }
        }
        background: Rectangle { color: window.panel; border.color: window.line }
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 28
            spacing: 14
            Image { source: window.selectedItem ? window.selectedItem.iconUrl : ""; Layout.preferredWidth: 82; Layout.preferredHeight: 82; fillMode: Image.PreserveAspectFit }
            Label { text: window.selectedItem ? window.selectedItem.name : ""; color: window.ink; font.pixelSize: 30; font.bold: true }
            Label { text: window.selectedItem ? window.selectedItem.summary : ""; color: window.ink; font.pixelSize: 17; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Label { text: window.selectedItem ? window.selectedItem.description : ""; color: window.muted; font.pixelSize: 14; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Label { text: window.selectedItem ? "Lizenz: " + window.selectedItem.license : ""; color: window.muted }
            Item { Layout.fillHeight: true }
            Button { Layout.fillWidth: true; text: window.selectedItem ? window.selectedItem.actionText : ""; enabled: window.selectedItem && window.selectedItem.actionEnabled && !window.storeBackend.busy; onClicked: window.storeBackend.installOrUpdate(window.selectedItem.id) }
            Button { Layout.fillWidth: true; text: "Projekt-Website"; onClicked: if (window.selectedItem) window.storeBackend.openUrl(window.selectedItem.homepage) }
            Button { Layout.fillWidth: true; text: "Quellcode"; onClicked: if (window.selectedItem) window.storeBackend.openUrl(window.selectedItem.source) }
            Button { Layout.fillWidth: true; text: "Schließen"; flat: true; onClicked: details.close() }
        }
    }
}
