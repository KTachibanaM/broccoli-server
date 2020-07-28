import React from "react";

const DivTable = (props) => {
  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
    }}>
      {props.children}
    </div>
  );
};

const DivTableRow = (props) => {
  return (
    <div style={{
      display: "flex",
      flexDirection: "row",
    }}>
      {props.children}
    </div>
  );
};

interface DivTableHeaderCellProps {
  hidden?: boolean;
  text: string;
  widthPx: number;
}

const DivTableHeaderCell = (props: DivTableHeaderCellProps) => {
  const hidden = props.hidden === undefined ? false : props.hidden;
  const display = hidden ? "none" : "flex";
  return (
    <div style={{
      display,
      width: `${props.widthPx}px`,
      justifyContent: "center",
    }}>
      {props.text}
    </div>
  );
};

interface DivTableCellProps {
  hidden?: boolean;
  children: any;
  widthPx: number;
}

const DivTableCell = (props: DivTableCellProps) => {
  const hidden = props.hidden === undefined ? false : props.hidden;
  const display = hidden ? "none" : "flex";
  return (
    <div style={{
      display,
      width: `${props.widthPx}px`,
      height: "400px",
      justifyContent: "center",
      alignItems: "center",
    }}>
      {props.children}
    </div>
  );
};

export {
  DivTable,
  DivTableRow,
  DivTableHeaderCell,
  DivTableCell,
};
