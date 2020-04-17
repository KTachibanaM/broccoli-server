import React from "react";
import { Subtract } from "utility-types";
import getDisplayName from "./getDisplayName";

export interface InjectedMessageProps {
  showOkMessage: (message: string) => void;
  showErrorMessage: (e: Error) => void;
}

const withMessage = <P extends InjectedMessageProps>(OriginalComponent: React.ComponentType<P>) => {
  type Props = Subtract<P, InjectedMessageProps>;

  interface State {
    message: string;
    messageStatus: "ok" | "error" | "";
  }

  class NewComponent extends React.Component<Props, State> {
    constructor(props: Props) {
      super(props);
      this.state = {
        message: "",
        messageStatus: "",
      };
    }

    public showOkMessage = (message: string) => {
      this.setState({
        message,
        messageStatus: "ok",
      });
    }

    public showErrorMessage = (message: string) => {
      this.setState({
        message,
        messageStatus: "error",
      });
    }

    public render() {
      return (
        <div>
          <OriginalComponent
            showOkMessage={this.showOkMessage}
            showErrorMessage={this.showErrorMessage}
            {...this.props as P}
          />
          {this.state.message ?
            (<div style={{
              color: this.state.messageStatus === "ok" ? "black" : "red",
            }}>{this.state.message}</div>) : null
          }
        </div>
      );
    }
  }

  (NewComponent as any).displayName = `applyMessage(${getDisplayName(OriginalComponent)})`;
  return NewComponent;
};

export default withMessage;
