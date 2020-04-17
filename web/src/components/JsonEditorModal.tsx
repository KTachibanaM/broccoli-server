import { JsonEditor as Editor } from "jsoneditor-react";
import "jsoneditor-react/es/editor.min.css";
import React from "react";
import Modal from "react-modal";

interface IProps {
  value: object;
  onValueChange: (newValue: object) => void;
  onClose: () => void;
  isOpen: boolean;
}

const JsonEditorModal: React.FunctionComponent<IProps> = (props: IProps) => {
  return (
    <Modal
      isOpen={props.isOpen}
      ariaHideApp={false}
    >
      <Editor
        value={props.value}
        onChange={props.onValueChange}
      />
      <button onClick={props.onClose}>Close</button>
    </Modal>
  );
};

export default JsonEditorModal;
