import qs from "query-string";
import React from "react";
import { RouteComponentProps, withRouter } from "react-router-dom";
import BoardProjection from "../../api/BoardProjection";
import JsonEditorModal from "../../components/JsonEditorModal";
import withAuth, { InjectedAuthProps } from "../../hoc/withAuth";
import withMessage, { InjectedMessageProps } from "../../hoc/withMessage";
import withRouting, { InjectedRoutingProps } from "../../hoc/withRouting";

type Props = InjectedAuthProps & InjectedMessageProps & InjectedRoutingProps & RouteComponentProps;

interface StateBoardProjection {
  name: string;
  module: string;
  className: string;
  args: object;
}

interface State {
  loading: boolean;
  name: string;
  q: object;
  limit: number;
  sort: object;
  projections: StateBoardProjection[];
  newProjectionName: string;
  newProjectionModule: string;
  newProjectionClassName: string;
  newProjectionArgs: object;
  modalIsOpen: boolean;
  modalIsEditing: "query" | "sort" | "newProjectionArgs";
}

class UpsertBoardPage extends React.Component<Props, State> {
  private boardId: string = "";
  private isNewBoard: boolean = true;

  constructor(props: Props) {
    super(props);

    const boardId = qs.parse(this.props.location.search).name;
    if (typeof boardId === "string") {
      this.boardId = boardId as string;
      this.isNewBoard = false;
    }
    this.state = {
      loading: !this.isNewBoard,
      name: "",
      q: {},
      limit: 0,
      sort: {},
      projections: [],
      newProjectionName: "",
      newProjectionModule: "",
      newProjectionClassName: "",
      newProjectionArgs: {},
      modalIsOpen: false,
      modalIsEditing: "query",
    };

    this.onSubmit = this.onSubmit.bind(this);
    this.onAddProjection = this.onAddProjection.bind(this);
    this.onRemoveProjection = this.onRemoveProjection.bind(this);
    this.onMoveUpProjection = this.onMoveUpProjection.bind(this);
    this.onMoveDownProjection = this.onMoveDownProjection.bind(this);
  }

  public componentDidMount() {
    if (!this.isNewBoard) {
      this.props.apiClient.getBoard(this.boardId)
        .then((data) => {
          this.setState({
            loading: false,
            name: this.boardId,
            q: data.q,
            limit: data.limit ? data.limit : 0,
            sort: data.sort || {},
            projections: data.projections.map((p) => {
              return {
                name: p.name,
                module: p.module,
                className: p.class_name,
                args: p.args,
              };
            }),
          });
        })
        .catch((error) => {
          this.props.showErrorMessage(
            new Error(`Fail to load mod view query from board id, error ${error.toString()}`),
          );
        });
    }
  }

  public onSubmit(e) {
    this.submit();
    e.preventDefault();
  }

  public submit() {
    const {name, q, limit, sort, projections} = this.state;
    this.props.apiClient.upsertBoard(
      name,
      q,
      limit !== 0 ? limit : undefined,
      sort !== {} ? sort : undefined,
      projections.map((p) => {
        return {
          name: p.name,
          module: p.module,
          class_name: p.className,
          args: p.args,
        };
      }))
        .then(() => {
          this.props.redirectTo("/boards/view");
        })
        .catch((error) => {
          this.props.showErrorMessage(
            new Error(`Fail to submit, error ${error.toString()}`),
          );
        });
  }

  public onAddProjection(e) {
    this.addProjection();
    e.preventDefault();
  }

  public addProjection() {
    this.setState({
      projections: this.state.projections.concat([{
        name: this.state.newProjectionName,
        module: this.state.newProjectionModule,
        className: this.state.newProjectionClassName,
        args: this.state.newProjectionArgs,
      }]),
      newProjectionName: "",
      newProjectionModule: "",
      newProjectionClassName: "",
      newProjectionArgs: {},
    });
  }

  public onRemoveProjection(e, name) {
    this.removeProjection(name);
    e.preventDefault();
  }

  public removeProjection(name) {
    this.setState({
      ...this.state,
      projections: this.state.projections.filter((p) => {
        return p.name !== name;
      }),
    });
  }

  public onMoveUpProjection(e, index) {
    this.moveUpProjection(index);
    e.preventDefault();
  }

  public moveUpProjection(index) {
    const projections = this.state.projections;
    [projections[index - 1], projections[index]] = [projections[index], projections[index - 1]];
    this.setState({
      ...this.state,
      projections,
    });
  }

  public onMoveDownProjection(e, index) {
    this.moveDownProjection(index);
    e.preventDefault();
  }

  public moveDownProjection(index) {
    const projections = this.state.projections;
    [projections[index], projections[index + 1]] = [projections[index + 1], projections[index]];
    this.setState({
      ...this.state,
      projections,
    });
  }

  public render() {
    if (this.state.loading) {
      return (<div>Loading...</div>);
    }
    return (
      <div>
        <b>Create new mod view</b>
        <div>
          Name:<br/>
          <input
            type="text"
            value={this.state.name}
            onChange={(e) => (this.setState({name: e.target.value}))}
          /><br/>
          Query:<br/>
          <button onClick={() => {
            this.setState({
              modalIsOpen: true,
              modalIsEditing: "query",
            });
          }}>Open JSON editor</button>
          <div>{JSON.stringify(this.state.q)}</div>
          Limit (0 to unset):<br/>
          <input
            type="number"
            value={this.state.limit}
            onChange={(e) => (this.setState({limit: parseInt(e.target.value, 10)}))}
          /><br/>
          Sort:<br/>
          <button onClick={() => {
            this.setState({
              modalIsOpen: true,
              modalIsEditing: "sort",
            });
          }}>Open JSON editor</button>
          <div>{JSON.stringify(this.state.sort)}</div>
          Columns:<br/>
          <table>
            <thead>
            <tr>
              <th>Name</th>
              <th>Module</th>
              <th>Class Name</th>
              <th>Args</th>
              <th/>
            </tr>
            </thead>
            <tbody>
            <tr>
              <td>
                <input
                  type="text"
                  value={this.state.newProjectionName}
                  onChange={(e) => (this.setState({newProjectionName: e.target.value}))}
                />
              </td>
              <td>
                <input
                  type="text"
                  size={63}
                  value={this.state.newProjectionModule}
                  onChange={(e) => (this.setState({newProjectionModule: e.target.value}))}
                />
              </td>
              <td>
                <input
                  type="text"
                  value={this.state.newProjectionClassName}
                  onChange={(e) => (this.setState({newProjectionClassName: e.target.value}))}
                />
              </td>
              <td>
                <button onClick={() => {
                  this.setState({
                    modalIsOpen: true,
                    modalIsEditing: "newProjectionArgs",
                  });
                }}>Open JSON editor</button>
                <div>{JSON.stringify(this.state.newProjectionArgs)}</div>
              </td>
              <td>
                <button onClick={(e) => this.onAddProjection(e)}>+</button>
              </td>
            </tr>
            {this.state.projections.map((projection, index) => {
              const {name, module, className, args} = projection;
              return (
                <tr key={name}>
                  <td>{name}</td>
                  <td>{module}</td>
                  <td>{className}</td>
                  <td>{JSON.stringify(args)}</td>
                  <td>
                    {index !== 0 ? <button onClick={(e) => {this.onMoveUpProjection(e, index); }}>↑</button> : null}
                    {index !== this.state.projections.length - 1
                      ? <button onClick={(e) => {this.onMoveDownProjection(e, index); }}>↓</button>
                      : null
                    }
                    <button onClick={(e) => this.onRemoveProjection(e, name)}>-</button>
                  </td>
                </tr>
              );
            })}
            </tbody>
          </table>
          <button onClick={this.onSubmit}>Submit</button>
        </div>
        <JsonEditorModal
          value={
            this.state.modalIsEditing === "query"
              ? this.state.q :
            this.state.modalIsEditing === "sort"
              ? this.state.sort :
            this.state.modalIsEditing === "newProjectionArgs"
              ? this.state.newProjectionArgs : {}
          }
          onValueChange={(newValue) => {
            if (this.state.modalIsEditing === "query") {
              this.setState({q: newValue});
            } else if (this.state.modalIsEditing === "sort") {
              this.setState({sort: newValue});
            } else if (this.state.modalIsEditing === "newProjectionArgs") {
              this.setState({newProjectionArgs: newValue});
            }
          }}
          onClose={() => {this.setState({modalIsOpen: false}); }}
          isOpen={this.state.modalIsOpen}
        />
      </div>
    );
  }
}

export default withAuth(
  withRouting(
    withMessage(
      withRouter(UpsertBoardPage),
    ),
  ),
);
