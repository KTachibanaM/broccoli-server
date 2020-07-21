import React from "react";
import {RouteComponentProps, withRouter} from "react-router-dom";
import BoardRender, {ActionableRenderTypes, RenderDataTypes, RenderTypes, Row} from "../../api/BoardRender";
import { InjectedAuthProps } from "../../hoc/withAuth";
import { InjectedMessageProps } from "../../hoc/withMessage";
import { InjectedRoutingProps } from "../../hoc/withRouting";
import Button from "../modView/columnRenders/Button";
import Image from "../modView/columnRenders/Image";
import ImageList from "../modView/columnRenders/ImageList";
import Text from "../modView/columnRenders/Text";
import Video from "../modView/columnRenders/Video";
import {DivTable, DivTableCell, DivTableHeaderCell, DivTableRow} from "./DivTable";

interface Params {
  name: string;
}

type Props = InjectedAuthProps & InjectedMessageProps & InjectedRoutingProps & RouteComponentProps<Params>;

interface State {
  loading: boolean;
  boardRender: BoardRender | {};
  multiActionOn: boolean;
  multiActionSelectedIndexes: Set<number>;
  multiActionLastSelectedIndex: number;
  holdingShift: boolean;
}

class Board extends React.Component<Props, State> {
  private static InitialState = {
    loading: true,
    boardRender: {},
    multiActionOn: false,
    multiActionSelectedIndexes: new Set<number>(),
    multiActionLastSelectedIndex: -1,
    holdingShift: false,
  };
  private readonly boardId: string;

  constructor(props: Props) {
    super(props);
    this.boardId = decodeURIComponent(this.props.match.params.name);
    this.state = Board.InitialState;
  }

  loadQuery = () => {
    this.setState(Board.InitialState);
    this.props.apiClient.renderBoard(this.boardId)
      .then(boardRender => this.setState({ boardRender }))
      .catch((error) => {
        this.props.showErrorMessage(
          new Error(`Fail to load mod view, error ${error.toString()}`),
        );
      })
      .finally(() => {
        this.setState({
          loading: false,
        });
      });
  }

  public componentDidMount() {
    document.addEventListener("keydown", this.keyDown, false);
    document.addEventListener("keyup", this.keyUp, false);
    this.loadQuery();
  }

  public componentWillUnmount(): void {
    document.removeEventListener("keydown", this.keyDown, false);
    document.removeEventListener("keyup", this.keyUp, false);
  }

  public renderColumn = (
    type: RenderTypes,
    data: RenderDataTypes,
    rawDocument?: object,
    callbackId?: string,
    getRawDocument?: () => object[],
  ) => {
    let ColumnComponent;
    if (type === "text") {
      ColumnComponent = Text;
    } else if (type === "image") {
      ColumnComponent = Image;
    } else if (type === "image_list") {
      ColumnComponent = ImageList;
    } else if (type === "button") {
      ColumnComponent = Button;
    } else if (type === "video") {
      ColumnComponent = Video;
    }
    if (!ColumnComponent) {
      return <div>`Unknown column type ${type}`</div>;
    }
    return <ColumnComponent
      data={data}
      callbackId={callbackId}
      rawDocument={rawDocument}
      getRawDocument={getRawDocument}
      apiClient={this.props.apiClient}
      reload={this.loadQuery}
    />;
  }

  public getColumnWidthPx = (type: RenderTypes) => {
    if (type === "text") {
      return 400;
    } else if (type === "image") {
      return 400;
    } else if (type === "image_list") {
      return 400;
    } else if (type === "button") {
      return 100;
    } else if (type === "video") {
      return 400;
    }
    return 100;
  }

  public onToggleRowMultiAction = (index: number) => {
    const newSelectedIndexes = new Set<number>(this.state.multiActionSelectedIndexes.values());
    if (newSelectedIndexes.has(index)) {
      newSelectedIndexes.delete(index);
    } else {
      newSelectedIndexes.add(index);
      const lastSelectedIndex = this.state.multiActionLastSelectedIndex;
      if (this.state.holdingShift
        && lastSelectedIndex !== -1
        && lastSelectedIndex < index
      ) {
        for (let i = lastSelectedIndex; i < index + 1; i++) {
          newSelectedIndexes.add(i);
        }
      }
      this.setState({
        multiActionLastSelectedIndex: index,
      });
    }
    this.setState({
      multiActionSelectedIndexes: newSelectedIndexes,
    });
  }

  public renderRow = (projectionNames: string[], row: Row, rowIndex: number) => {
    const rowRenders = row.renders;
    return (
      <DivTableRow key={rowIndex}>
        <DivTableCell
          hidden={!this.state.multiActionOn}
          key="multi-action-selected"
          widthPx={50}
        >
          <input
            type="checkbox"
            checked={this.state.multiActionSelectedIndexes.has(rowIndex)}
            onChange={() => {
              this.onToggleRowMultiAction(rowIndex);
            }}
          />
        </DivTableCell>
        {projectionNames.map((name) => {
          const rowRender = rowRenders[name];
          let cell;
          if (!rowRender) {
            cell = (<div>N/A</div>);
          } else {
            cell = this.renderColumn(
              rowRender.type,
              rowRender.data,
              row.raw_document,
              rowRender.callback_id,
            );
          }
          return (
            <DivTableCell
              key={name}
              widthPx={this.getColumnWidthPx(rowRender.type)}
            >{cell}</DivTableCell>
          );
        })}
      </DivTableRow>
    );
  }

  public renderPayload = () => {
    const boardRender: BoardRender = this.state.boardRender as BoardRender;
    const {payload} = boardRender;
    if (!payload || payload.length === 0) {
      return (
        <div>Query is empty</div>
      );
    }
    const projectionNames = (this.state.boardRender as BoardRender).board_query.projections.map((p) => p.name);
    return (
      <div>
        <div>Query count: {boardRender.count_without_limit}</div>
        <div>
          <input type="checkbox" id="toggleMultiAction" onClick={this.onToggleMultiAction}/>
          <label htmlFor="toggleMultiAction">Toggle multi-action</label>
        </div>
        <div hidden={!this.state.multiActionOn}>
          Multi-action: selected {this.state.multiActionSelectedIndexes.size} items
          {this.renderRangeSelectPrompt()}
          {this.renderMultiActions()}
        </div>
        <DivTable>
          <DivTableRow>
            <DivTableHeaderCell
              key="multi-action-selected"
              text="Multi-action selected"
              hidden={!this.state.multiActionOn}
              widthPx={50}
            />
            {projectionNames.map((name) =>
              <DivTableHeaderCell
                key={name}
                text={name}
                widthPx={this.getColumnWidthPx(payload[0].renders[name].type)}
              />,
            )}
          </DivTableRow>
          {payload.map((row, index) => {
            return this.renderRow(projectionNames, row, index);
          })}
        </DivTable>
      </div>
    );
  }

  public onToggleMultiAction = () => {
    this.setState({
      multiActionOn: !this.state.multiActionOn,
    });
  }

  public renderRangeSelectPrompt = () => {
    if (this.state.holdingShift) {
      return (<div>Range selecting</div>);
    } else {
      return (<div>Hold "shift" to range select</div>);
    }
  }

  public renderMultiActions = () => {
    const boardRender = (this.state.boardRender as BoardRender);
    const payload = boardRender.payload;
    if (payload.length === 0) {
      return <div>No multi-action to render</div>;
    }
    const firstRowRenders = payload[0].renders;
    const projectionNames = boardRender.board_query.projections.map((p) => p.name);

    const headings = projectionNames.map((name) =>
      <th key={name}>{name}</th>,
    );

    const columns = projectionNames.map((name) => {
      const render = firstRowRenders[name];
      let cell;
      if (!render) {
        cell = (<div>N/A</div>);
      } else if (!ActionableRenderTypes.has(render.type)) {
        cell = (<div>Not action-able</div>);
      } else {
        cell = this.renderColumn(
          render.type,
          render.data,
          undefined,
          render.callback_id,
          () => {
            return Array.from(this.state.multiActionSelectedIndexes).map((index) => {
              return payload[index].raw_document;
            });
          },
        );
      }
      return (
        <td key={name}>{cell}</td>
      );
    });
    return (
      <table>
        <thead>
          <tr>
            {headings}
          </tr>
        </thead>
        <tbody>
          <tr>
            {columns}
          </tr>
        </tbody>
      </table>
    );
  }

  public keyDown = (e) => {
    if (e.keyCode === 16 && this.state.multiActionOn) {
      this.setState({
        holdingShift: true,
      });
    }
  }

  public keyUp = (e) => {
    if (e.keyCode === 16 && this.state.multiActionOn) {
      this.setState({
        holdingShift: false,
      });
    }
  }

  public render() {
    if (this.state.loading) {
      return (<div>Loading mod view...</div>);
    }
    const boardRender: BoardRender = this.state.boardRender as BoardRender;
    return (
      <div>
        <b>Mod view "{this.boardId}"</b>
        <div>Query: {JSON.stringify(boardRender.board_query.q)}</div>
        <div>Limit: {boardRender.board_query.limit ? boardRender.board_query.limit : "N/A"}</div>
        <div>Sort: {boardRender.board_query.sort ? JSON.stringify(boardRender.board_query.sort) : "N/A"}</div>
        {this.renderPayload()}
      </div>
    );
  }
}

export default withRouter(Board);
