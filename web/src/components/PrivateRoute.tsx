import React from "react"
import {Route, Redirect} from "react-router-dom";
import ApiClient from "../api/ApiClient";

interface Props {
  render: () => JSX.Element,
  apiClient: ApiClient,
  path: string
}

const PrivateRoute: React.FC<Props> = ({render, apiClient, path}) => (
  <Route
    path={path}
    render={props => {
      if (apiClient.hasAuth()) {
        return render()
      }
      return (
        <Redirect to={{
          pathname: '/login',
          state: {from: props.location}
        }}/>
      )
    }}
  />
);

export default PrivateRoute
