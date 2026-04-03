import React from "react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";

export const GlobalDndContext = ({ key, children }) => {
  return (
    <DndProvider backend={HTML5Backend} key={key}>
      {children}
    </DndProvider>
  );
};
