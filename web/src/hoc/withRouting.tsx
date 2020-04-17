import React from "react";
import { Redirect } from "react-router-dom";
import { Subtract } from "utility-types";
import getDisplayName from "./getDisplayName";

export interface InjectedRoutingProps {
  redirectTo: (path: string) => void;
}

const withRouting = <P extends InjectedRoutingProps>(OriginalComponent: React.ComponentType<P>) => {
  type Props = Subtract<P, InjectedRoutingProps>;

  interface State {
    redirectTo: string;
  }

  class NewComponent extends React.Component<Props, State> {
    constructor(props: Props) {
      super(props);
      this.state = {
        redirectTo: "",
      };
    }

    public redirectTo = (path: string) => {
      this.setState({
        redirectTo: path,
      });
    }

    public render() {
      if (this.state.redirectTo) {
        return (<Redirect to={this.state.redirectTo}/>);
      }
      return (<OriginalComponent redirectTo={this.redirectTo} {...this.props as P} />);
    }
  }

  (NewComponent as any).displayName = `applyRouting(${getDisplayName(OriginalComponent)})`;
  return NewComponent;
};

export default withRouting;
