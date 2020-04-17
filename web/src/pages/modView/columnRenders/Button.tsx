import React from "react";
import ApiClient from "../../../api/ApiClient";

export interface ButtonData {
  text: string;
  reload_after_callback: boolean;
}

interface Props {
  data: ButtonData;
  callbackId: string;
  rawDocument?: object;
  getRawDocument?: () => object[];
  apiClient: ApiClient;
  reload: () => void;
}

const Button: React.FunctionComponent<Props> = (props: Props) => {
  const { data, callbackId, rawDocument, apiClient, reload, getRawDocument } = props;
  if (rawDocument === undefined && getRawDocument === undefined) {
    return <div>Neither rawDocument nor getRawDocument</div>;
  }
  const { text, reload_after_callback: reloadAfterCallback } = data;
  return (
    <button
      onClick={() => {
        let rawDocuments: object[];
        if (getRawDocument !== undefined) {
          rawDocuments = (getRawDocument as () => object[])();
        } else {
          rawDocuments = [(rawDocument as object)];
        }
        Promise.all(rawDocuments.map((d) =>
          apiClient.callbackBoard(callbackId, d),
        ))
          .catch((e) => {
            // TODO
          })
          .finally(() => {
            if (reloadAfterCallback) {
              reload();
            }
          });

      }}
    >{text}</button>
  );
};

export default Button;
