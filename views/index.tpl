% rebase('layout.tpl', title='Események')
<div class="jumbotron">
    <h1>Események</h1>
    <table class="table table-striped">
        <thead>
            <tr>
                <th>Időpont</th>
                <th>Kamera</th>
                <th>Méret</th>
                <th>Videó</th>
            </tr>
        </thead>
        <tbody>
        % for item in events:
            <tr>
                <td>{{item['time']}}</td>
                <td>{{item['camera']}}</td>
                <td>{{item['size']}}</td>
                <td><a href="{{item['url']}}">{{item['url']}}</a></td>
            </tr>
        % end
        </tbody>
    </table>
</div>

