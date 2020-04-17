import React from "react";
import { Subtract } from "utility-types";
import ApiClient from "../api/ApiClient";
import getDisplayName from "./getDisplayName";

export interface InjectedAuthProps {
  apiClient: ApiClient;
}

const withAuth = <P extends InjectedAuthProps>(OriginalComponent: React.ComponentType<P>) => {
  type Props = Subtract<P, InjectedAuthProps>;

  interface State {
    username: string;
    password: string;
  }

  class NewComponent extends React.Component<Props, State> {
    private apiClient: ApiClient;

    constructor(props: Props) {
      super(props);
      this.apiClient = new ApiClient();
      this.state = {
        username: "",
        password: "",
      };
    }

    public onSubmit = (e) => {
      this.submit();
      e.preventDefault();
    }

    public submit() {
      const {
        username,
        password,
      } = this.state;
      this.apiClient.auth(username, password)
        .then();
    }

    public render() {
      if (!this.apiClient.hasAuth()) {
        return (
          <div>
            <b>Log in</b>
            <div>
              Username:<br/>
              <input
                type="text"
                value={this.state.username}
                onChange={(e) => {this.setState({username: e.target.value}); }}
              /><br/>
              Password:<br/>
              <input
                type="password"
                value={this.state.password}
                onChange={(e) => {this.setState({password: e.target.value}); }}
              /><br/>
              <button onClick={this.onSubmit}>Submit</button>
            </div>
          </div>
        );
      }
      return (<OriginalComponent apiClient={this.apiClient} {...this.props as P} />);
    }
  }

  (NewComponent as any).displayName = `applyAuth(${getDisplayName(OriginalComponent)})`;
  return NewComponent;
};

export default withAuth;
