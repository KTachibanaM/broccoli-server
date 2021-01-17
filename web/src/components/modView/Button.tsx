import React from "react";
import ApiClient from "../../api/ApiClient";
import { Button as MuiButton } from "@material-ui/core"

export interface ButtonData {
  text: string;
  reload_after_callback: boolean;
}

interface Props {
  data: ButtonData;
  boardId: string;
  callbackId: string;
  rawDocument?: object;
  getRawDocument?: () => object[];
  apiClient: ApiClient;
  reloading: () => void;
  reload: (BoardRender) => void;
  reloadFinished: () => void;
}

const Button: React.FunctionComponent<Props> = (props: Props) => {
  const { data, boardId, callbackId, rawDocument, apiClient, reloading, reload, reloadFinished, getRawDocument } = props;
  if (rawDocument === undefined && getRawDocument === undefined) {
    return <div>Neither rawDocument nor getRawDocument</div>;
  }
  const { text, reload_after_callback: reloadAfterCallback } = data;
  return (
    <MuiButton
      variant="contained"
      color="secondary"
      onClick={() => {
        let rawDocuments: object[];
        if (getRawDocument !== undefined) {
          rawDocuments = (getRawDocument as () => object[])();
        } else {
          rawDocuments = [(rawDocument as object)];
        }
        if (reloadAfterCallback) {
          reloading()
        }
        Promise.all(rawDocuments.map((d) =>
          apiClient.callbackBoard(boardId, callbackId, d),
        ))
          .then(responses => {
            // @ts-ignore
            const boardRenders = responses.map(r => r.data)
            if (reloadAfterCallback) {
              reload(boardRenders[boardRenders.length - 1])
            }
          })
          .catch((e) => {
            // TODO
          })
          .finally(() => {
            reloadFinished()
          })
      }}
    >{text}</MuiButton>
  );
};

export default Button;
